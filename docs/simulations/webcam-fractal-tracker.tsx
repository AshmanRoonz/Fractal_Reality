import React, { useState, useRef, useEffect } from 'react';
import { Camera, Square, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine } from 'recharts';

const WebcamFractalTracker = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentD, setCurrentD] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [fps, setFps] = useState(30);
  const [roiSize, setRoiSize] = useState(100);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const timeRef = useRef(0);

  // Higuchi algorithm implementation
  const calculateHiguchi = (timeSeries, kMax = 25) => {
    const n = timeSeries.length;
    if (n < kMax * 2) return null;

    const lengths = [];
    
    for (let k = 1; k <= kMax; k++) {
      let Lk = 0;
      
      for (let m = 1; m <= k; m++) {
        let Lm = 0;
        const maxIdx = Math.floor((n - m) / k);
        
        for (let i = 1; i <= maxIdx; i++) {
          Lm += Math.abs(timeSeries[m + i * k - 1] - timeSeries[m + (i - 1) * k - 1]);
        }
        
        Lm = (Lm * (n - 1)) / (maxIdx * k * k);
        Lk += Lm;
      }
      
      Lk = Lk / k;
      lengths.push({ k, L: Lk });
    }

    // Linear regression on log-log plot
    const logData = lengths.map(d => ({
      x: Math.log(d.k),
      y: Math.log(d.L)
    }));

    const n_points = logData.length;
    const sumX = logData.reduce((sum, d) => sum + d.x, 0);
    const sumY = logData.reduce((sum, d) => sum + d.y, 0);
    const sumXY = logData.reduce((sum, d) => sum + d.x * d.y, 0);
    const sumX2 = logData.reduce((sum, d) => sum + d.x * d.x, 0);

    const slope = (n_points * sumXY - sumX * sumY) / (n_points * sumX2 - sumX * sumX);
    
    // Apply calibration: D = Higuchi - 0.3 (from your O3/O4 analysis)
    const rawD = -slope;
    const calibratedD = rawD - 0.3;
    
    return calibratedD;
  };

  // Extract brightness time series from video frame
  const extractTimeSeries = (canvas, video) => {
    const ctx = canvas.getContext('2d');
    const centerX = video.videoWidth / 2;
    const centerY = video.videoHeight / 2;
    const halfSize = roiSize / 2;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const imageData = ctx.getImageData(
      centerX - halfSize,
      centerY - halfSize,
      roiSize,
      roiSize
    );
    
    const timeSeries = [];
    
    // Extract brightness values (grayscale)
    for (let i = 0; i < imageData.data.length; i += 4) {
      const r = imageData.data[i];
      const g = imageData.data[i + 1];
      const b = imageData.data[i + 2];
      const brightness = 0.299 * r + 0.587 * g + 0.114 * b;
      timeSeries.push(brightness);
    }
    
    return timeSeries;
  };

  // Process frame and calculate D
  const processFrame = () => {
    if (!videoRef.current || !canvasRef.current || !isStreaming) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      const timeSeries = extractTimeSeries(canvas, video);
      const D = calculateHiguchi(timeSeries);
      
      if (D !== null && !isNaN(D)) {
        setCurrentD(D);
        
        const now = Date.now();
        timeRef.current += 1;
        
        setHistoryData(prev => {
          const newData = [...prev, { 
            time: timeRef.current,
            D: D,
            timestamp: now
          }].slice(-120); // Keep last 120 samples (4 seconds at 30fps)
          return newData;
        });
      }
    }

    animationRef.current = setTimeout(() => processFrame(), 1000 / fps);
  };

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: 640, 
          height: 480,
          frameRate: fps 
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setIsStreaming(true);
        timeRef.current = 0;
      }
    } catch (err) {
      console.error("Error accessing webcam:", err);
      alert("Could not access webcam. Please grant camera permissions.");
    }
  };

  const stopWebcam = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (animationRef.current) {
      clearTimeout(animationRef.current);
    }
    setIsStreaming(false);
    setCurrentD(null);
    setHistoryData([]);
    timeRef.current = 0;
  };

  useEffect(() => {
    if (isStreaming && videoRef.current) {
      videoRef.current.onloadedmetadata = () => {
        videoRef.current.play();
        processFrame();
      };
    }
  }, [isStreaming]);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (animationRef.current) {
        clearTimeout(animationRef.current);
      }
    };
  }, []);

  const getColorForD = (d) => {
    if (!d) return '#6b7280';
    const deviation = Math.abs(d - 1.5);
    if (deviation < 0.1) return '#10b981'; // green - close to 1.5
    if (deviation < 0.2) return '#f59e0b'; // amber - moderate
    return '#ef4444'; // red - far from 1.5
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl shadow-2xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
          <Activity className="text-cyan-400" />
          Webcam Fractal Dimension Tracker
        </h1>
        <p className="text-slate-300">
          Real-time measurement of fractal dimension D using Higuchi algorithm
        </p>
        <p className="text-sm text-cyan-400 mt-1">
          Framework prediction: D ≈ 1.5 at measurement interfaces
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Video Feed */}
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="relative">
            <video
              ref={videoRef}
              className="w-full rounded-lg bg-black"
              autoPlay
              playsInline
              muted
            />
            <canvas
              ref={canvasRef}
              width="640"
              height="480"
              className="hidden"
            />
            {isStreaming && (
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <Square 
                  size={roiSize} 
                  className="text-cyan-400 opacity-50"
                  strokeWidth={2}
                />
              </div>
            )}
          </div>
          
          <div className="mt-4 flex gap-3">
            {!isStreaming ? (
              <button
                onClick={startWebcam}
                className="flex-1 bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition"
              >
                <Camera size={20} />
                Start Tracking
              </button>
            ) : (
              <button
                onClick={stopWebcam}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-semibold transition"
              >
                Stop
              </button>
            )}
          </div>

          {/* Settings */}
          <div className="mt-4 space-y-3">
            <div>
              <label className="text-sm text-slate-300 block mb-1">
                ROI Size: {roiSize}px
              </label>
              <input
                type="range"
                min="50"
                max="200"
                value={roiSize}
                onChange={(e) => setRoiSize(parseInt(e.target.value))}
                className="w-full"
                disabled={isStreaming}
              />
            </div>
            <div>
              <label className="text-sm text-slate-300 block mb-1">
                FPS: {fps}
              </label>
              <input
                type="range"
                min="10"
                max="60"
                value={fps}
                onChange={(e) => setFps(parseInt(e.target.value))}
                className="w-full"
                disabled={isStreaming}
              />
            </div>
          </div>
        </div>

        {/* Current D Display */}
        <div className="bg-slate-800 rounded-lg p-4 flex flex-col">
          <h2 className="text-xl font-semibold text-white mb-4">Current Measurement</h2>
          
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl font-bold mb-2" style={{ color: getColorForD(currentD) }}>
                {currentD ? currentD.toFixed(3) : '---'}
              </div>
              <div className="text-slate-400 text-sm">Fractal Dimension (D)</div>
              
              {currentD && (
                <div className="mt-4 space-y-2">
                  <div className="text-lg">
                    <span className="text-slate-400">Deviation from 1.5: </span>
                    <span className="font-semibold text-white">
                      {Math.abs(currentD - 1.5).toFixed(3)}
                    </span>
                  </div>
                  <div className="text-sm text-slate-300">
                    {Math.abs(currentD - 1.5) < 0.1 
                      ? '✓ Within framework prediction' 
                      : Math.abs(currentD - 1.5) < 0.2
                      ? '~ Near framework prediction'
                      : '✗ Outside framework prediction'}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-4 bg-slate-900 rounded p-3 text-sm text-slate-300">
            <div className="font-semibold text-white mb-2">Reference Values:</div>
            <div>• GW O3/O4: D = 1.49 ± 0.04</div>
            <div>• Framework: D ≈ 1.5</div>
            <div>• Calibration: D = Higuchi - 0.3</div>
          </div>
        </div>
      </div>

      {/* Time Series Chart */}
      {historyData.length > 0 && (
        <div className="bg-slate-800 rounded-lg p-4">
          <h2 className="text-xl font-semibold text-white mb-4">
            D Evolution (Last 4 seconds)
          </h2>
          <LineChart width={1000} height={300} data={historyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis 
              dataKey="time" 
              stroke="#94a3b8"
              label={{ value: 'Frame', position: 'insideBottom', offset: -5, fill: '#94a3b8' }}
            />
            <YAxis 
              domain={[1.0, 2.0]}
              stroke="#94a3b8"
              label={{ value: 'D', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
              labelStyle={{ color: '#94a3b8' }}
            />
            <Legend />
            <ReferenceLine y={1.5} stroke="#06b6d4" strokeDasharray="5 5" label="Framework (1.5)" />
            <Line 
              type="monotone" 
              dataKey="D" 
              stroke="#06b6d4" 
              strokeWidth={2}
              dot={false}
              name="Fractal Dimension"
            />
          </LineChart>
        </div>
      )}
    </div>
  );
};

export default WebcamFractalTracker;