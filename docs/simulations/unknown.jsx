import React, { useRef, useEffect, useState } from "react";

export default function WholenessSimulator() {
  const canvasRef = useRef(null);
  const [beta, setBeta] = useState(0.5); // convergence-emergence balance

  useEffect(() => {
    const ctx = canvasRef.current.getContext("2d");
    const particles = Array.from({ length: 400 }, () => ({
      r: Math.random() * 300,
      a: Math.random() * 2 * Math.PI,
      phase: Math.random() * 100,
    }));
    let t = 0;

    function draw() {
      const { width, height } = canvasRef.current;
      ctx.fillStyle = "rgba(0,0,20,0.2)";
      ctx.fillRect(0, 0, width, height);

      const cx = width / 2, cy = height / 2;
      const ringR = 120 + 40 * Math.sin(t * 0.02);

      // draw infinite field glow
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, width/2);
      grad.addColorStop(0, `hsla(${240 + 60 * Math.sin(t*0.01)},100%,70%,0.6)`);
      grad.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      // draw interface ring
      ctx.beginPath();
      ctx.strokeStyle = `hsla(180,100%,70%,0.5)`;
      ctx.lineWidth = 2;
      ctx.arc(cx, cy, ringR, 0, 2 * Math.PI);
      ctx.stroke();

      // draw particles moving through ICE
      particles.forEach(p => {
        const dir = p.r > ringR ? -1 : 1;
        p.r += dir * (0.6 - 0.4 * beta) * Math.sin(t*0.01 + p.phase);
        p.a += 0.005 * (1.2 - beta);
        const x = cx + p.r * Math.cos(p.a);
        const y = cy + p.r * Math.sin(p.a);
        ctx.fillStyle = `hsla(${200 + 100*Math.sin(p.phase + t*0.05)},100%,70%,0.8)`;
        ctx.beginPath();
        ctx.arc(x, y, 1.5, 0, 2 * Math.PI);
        ctx.fill();
      });

      // central convergence pulse
      ctx.beginPath();
      ctx.fillStyle = `hsla(${300+60*Math.sin(t*0.05)},100%,80%,0.8)`;
      ctx.arc(cx, cy, 8 + 4*Math.sin(t*0.1), 0, 2*Math.PI);
      ctx.fill();

      t += 1;
      requestAnimationFrame(draw);
    }
    draw();
  }, [beta]);

  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      <canvas ref={canvasRef} width={800} height={800} className="rounded-2xl shadow-lg" />
      <div className="mt-4 flex gap-4">
        <label>β = {beta.toFixed(2)}</label>
        <input type="range" min="0" max="1" step="0.01"
          value={beta}
          onChange={e => setBeta(parseFloat(e.target.value))}
        />
      </div>
    </div>
  );
}
