// The book read aloud. One recording, joined from ElevenLabs (eleven_v4) generations of
// narration/narration-script.txt in the author's cloned voice: three parts for the pages, plus the
// title page invitation spliced in after the subtitle. starts[i] is the second at which page i
// turns: the middle of the pause before its first words, found by aligning silences to each page's
// text length.
window.NARRATION = {
  src: 'audio/existence-narration.mp3',
  reader: 'Ashman Roonz',
  duration: 947.62,
  starts: [0, 31.63, 34.39, 37.89, 49.1, 60.54, 64.38, 68.42, 80.28, 84.78, 92.97, 103.74, 114.78, 118.63,
    130.74, 134.75, 142.37, 162.39, 181.78, 185.4, 196.73, 200.24, 228.68, 231.6, 241.3, 250.67, 254.32,
    257.52, 289.96, 310.2, 332.25, 345.89, 350.41, 363.86, 369.58, 396.88, 411.41, 427.46, 448.41, 452.97,
    457.06, 478.52, 498.21, 522.66, 536.33, 542.51, 563.21, 578.55, 585.37, 590.76, 599.42, 624.66, 631.34,
    657.74, 675.38, 690.32, 695.21, 710.99, 725.36, 746.71, 756.56, 779.96, 787.47, 793.78, 807.47, 822.99,
    857.23, 876.52, 883.27, 898.61, 909.06, 914.97, 931.42, 934.59, 942.8]
};
