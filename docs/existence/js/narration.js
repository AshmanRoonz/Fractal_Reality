// The book read aloud in the author's cloned voice, as one recording per track, played in order.
// Each recording is joined from ElevenLabs (eleven_v4) generations of a script in narration/:
// Part One from narration-script.txt (three parts, plus the title page invitation spliced in after
// the subtitle), Part Two from part-two/script.txt. A track covers pages first .. first +
// starts.length - 1, and starts[j] is the second at which page first + j turns: the middle of the
// pause before its first words, found by aligning silences to each page's text length.
window.NARRATION = {
  reader: 'Ashman Roonz',
  tracks: [
    { src: 'audio/existence-narration.mp3', first: 0, duration: 947.62,
      starts: [0, 31.63, 34.39, 37.89, 49.1, 60.54, 64.38, 68.42, 80.28, 84.78, 92.97, 103.74, 114.78, 118.63,
        130.74, 134.75, 142.37, 162.39, 181.78, 185.4, 196.73, 200.24, 228.68, 231.6, 241.3, 250.67, 254.32,
        257.52, 289.96, 310.2, 332.25, 345.89, 350.41, 363.86, 369.58, 396.88, 411.41, 427.46, 448.41, 452.97,
        457.06, 478.52, 498.21, 522.66, 536.33, 542.51, 563.21, 578.55, 585.37, 590.76, 599.42, 624.66, 631.34,
        657.74, 675.38, 690.32, 695.21, 710.99, 725.36, 746.71, 756.56, 779.96, 787.47, 793.78, 807.47, 822.99,
        857.23, 876.52, 883.27, 898.61, 909.06, 914.97, 931.42, 934.59, 942.8] },
    { src: 'audio/existence-narration-part2.mp3', first: 75, duration: 948.61,
      starts: [0, 20.32, 39.9, 59.17, 79.6, 100.21, 123.33, 146.55, 167.67, 191.85, 219.52, 245.96, 268.17,
        292.46, 316.6, 340.61, 362.86, 384.42, 405.94, 435.81, 457.09, 478.68, 500.48, 522.14, 539.94, 559.05,
        590.14, 613.99, 640.46, 674.68, 698.29, 720.1, 744.49, 767.28, 788.43, 811.89, 831.55, 851.3, 875.9,
        898.54, 920.2] }
  ]
};
