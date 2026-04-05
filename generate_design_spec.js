const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, WidthType, BorderStyle, ShadingType,
        VerticalAlign, HeadingLevel, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 22 }  // 11pt default
      }
    },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1F4E78" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 }
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E5C8A" },
        paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 }
      },
      {
        id: "Heading3",
        name: "Heading 3",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "3D6BA6" },
        paragraph: { spacing: { before: 120, after: 80 }, outlineLevel: 2 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: {
          width: 12240,   // US Letter width
          height: 15840   // US Letter height
        },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }  // 1 inch margins
      }
    },
    headers: {
      default: new Header({
        children: [
          new Paragraph({
            children: [new TextRun({
              text: "Circumpunct Game Engine: Design Specification",
              size: 20,
              color: "666666"
            })],
            border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6", space: 1 } }
          })
        ]
      })
    },
    footers: {
      default: new Footer({
        children: [
          new Paragraph({
            children: [
              new TextRun({
                text: "Page ",
                size: 20,
                color: "666666"
              }),
              new TextRun({
                children: [PageNumber.CURRENT],
                size: 20,
                color: "666666"
              })
            ],
            alignment: AlignmentType.RIGHT
          })
        ]
      })
    },
    children: [
      // Title page
      new Paragraph({
        children: [new TextRun("")],
        spacing: { before: 400 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "Circumpunct Game Engine",
          size: 48,
          bold: true,
          color: "1F4E78"
        })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 120 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "Design Specification",
          size: 40,
          bold: true,
          color: "1F4E78"
        })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "A Framework-Native Physics Engine Built on E = 1",
          size: 28,
          italic: true,
          color: "2E5C8A"
        })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 }
      }),
      new Paragraph({
        children: [new TextRun("")],
        spacing: { before: 200 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "By Ashman Roonz",
          size: 24,
          color: "333333"
        })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 }
      }),
      new Paragraph({
        children: [new TextRun({
          text: "April 2026",
          size: 22,
          color: "666666"
        })],
        alignment: AlignmentType.CENTER
      }),

      // Page break
      new Paragraph({ children: [new PageBreak()] }),

      // Section 1: Foundational Principle
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("1. Foundational Principle")]
      }),
      new Paragraph({
        children: [new TextRun("E = 1. There is one energy. Everything in the engine is a constraint on that one energy. The engine does not simulate physics from outside; it IS physics, expressed through the circumpunct (the dot within the circle: aperture, field, boundary).")]
      }),
      new Paragraph({
        children: [new TextRun("Every object is a circumpunct. Every force is a constraint. Every frame is one iteration of the pump cycle. The total energy at every scale sums to 1 via softmax normalization.")],
        spacing: { after: 240 }
      }),

      // Section 2: Three-Layer Architecture
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("2. The Three-Layer Architecture")]
      }),
      new Paragraph({
        children: [new TextRun("The engine has three layers, mapping directly to the circumpunct:")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Boundary (3D, rendered)")]
      }),
      new Paragraph({
        children: [new TextRun("What the player sees. Meshes, terrain, objects, characters. This is what the GPU draws. The boundary is the body of every entity: its visible, tangible form.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Field (2D, computed but not rendered)")]
      }),
      new Paragraph({
        children: [new TextRun("The invisible substrate that shapes the boundary over time. Flow vectors, force fields, noise fields, erosion patterns, wind currents. This is what the CPU (or compute shaders) calculates. The field is never drawn directly; the player sees only its effects on the boundary.")]
      }),
      new Paragraph({
        children: [new TextRun("Why invisible? Because that is how reality works. You do not see wind; you see the tree bending. You do not see gravity; you see the apple falling. You do not see the field (Phi); you see what the field did to the boundary.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Aperture (0D, the player)")]
      }),
      new Paragraph({
        children: [new TextRun("Where the player looks determines what gets computed at high resolution. The aperture is the convergence point of attention. It selects which boundaries get rendered in detail and which field regions get computed at full fidelity.")],
        spacing: { after: 240 }
      }),

      // Section 3: Softmax
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("3. Softmax as Universal Constraint")]
      }),
      new Paragraph({
        children: [new TextRun("Softmax enforces E = 1 at every scale. It takes any vector of raw values and normalizes them so they sum to one. This is the circumpunct constraint in computational form.")]
      }),
      new Paragraph({
        children: [new TextRun("Applications across the engine:")],
        spacing: { after: 120 }
      }),

      // Softmax table
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "System", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "What softmax distributes", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Raw input", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Output", bold: true })], alignment: AlignmentType.CENTER })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Entity internals")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Energy across three constraints (soul, field, boundary)")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Raw constraint values")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Normalized triad summing to 1")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Render budget")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("GPU time across visible objects")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Inverse distance to camera")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Per-object render quality")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Compute budget")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("CPU time across field regions")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Inverse distance to aperture")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Per-region field resolution")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Fracture")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Energy across child fragments")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Random raw energies")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Per-fragment share of parent's E=1")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Attention allocation")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Total awareness across entities")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Proximity and resonance scores")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Per-entity tier assignment")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Network bandwidth")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Update rate across players")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Inverse latency")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Per-player sync frequency")] })]
              })
            ]
          })
        ]
      }),

      new Paragraph({
        children: [new TextRun("Temperature parameter: controls distribution sharpness. Low temperature = one dominant allocation (boss arena, single focus). High temperature = even spread (open world, distributed attention). Temperature maps to the balance parameter.")],
        spacing: { before: 120, after: 240 }
      }),

      // Section 4: Foveated Everything
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("4. Foveated Everything")]
      }),
      new Paragraph({
        children: [new TextRun("Not just foveated rendering; foveated physics, foveated AI, foveated audio, foveated networking. All driven by distance from the player's aperture.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Resolution Tiers")]
      }),

      // Resolution tiers table
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [1170, 1170, 1170, 1170, 1170, 1170, 1560],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun({ text: "Tier", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun({ text: "Name", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun({ text: "Compute", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun({ text: "Rendering", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun({ text: "Physics", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun({ text: "Field", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1560, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun({ text: "Example", bold: true })], alignment: AlignmentType.CENTER })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("3")], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("FULL")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("100%")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("High-poly, all effects")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Full pump cycle, all forces")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Full SRL adaptation")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1560, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Player looking at")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("2")], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("MID")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("~40%")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Mid-poly, reduced effects")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Simplified pump")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Reduced adaptation")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1560, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Nearby periphery")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("1")], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("LOW")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("~10%")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Low-poly, wireframe")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Slow balance drift")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Frozen field")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1560, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Distant visible")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("0")], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("DORMANT")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("~0%")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Minimal/none")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("No update")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1170, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Completely frozen")] })]
              }),
              new TableCell({
                borders,
                width: { size: 1560, type: WidthType.DXA },
                margins: { top: 60, bottom: 60, left: 80, right: 80 },
                children: [new Paragraph({ children: [new TextRun("Behind player")] })]
              })
            ]
          })
        ]
      }),

      new Paragraph({
        children: [new TextRun("The tier assignment uses softmax over inverse distance: each entity's share of the budget determines its tier. Two softmax budgets run in parallel: (1) Render budget (E = 1): distributed across visible boundaries, and (2) Compute budget (E = 1): distributed across field regions. Both are independent but driven by the same aperture position.")],
        spacing: { before: 120, after: 240 }
      }),

      // Section 5: Pump Cycle
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("5. The Pump Cycle as Universal Update Loop")]
      }),
      new Paragraph({
        children: [new TextRun("Every frame, the engine runs one iteration of the pump cycle: converge, rotate, emerge.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Convergence (gather)")]
      }),
      new Paragraph({
        children: [new TextRun("Collect input: player actions, sensor data, network state, field influences. Pull information inward toward the aperture.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Rotation (i-turn, process)")]
      }),
      new Paragraph({
        children: [new TextRun("Transform the gathered state. Apply forces, compute field evolution, run SRL adaptation, evaluate integrity. The 90-degree phase shift where raw input becomes processed state.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Emergence (output)")]
      }),
      new Paragraph({
        children: [new TextRun("Radiate results outward. Update boundary positions, render the frame, transmit network state, play audio. Push processed state out to the world.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        children: [new TextRun("This maps to the standard game loop (input, update, render) but with a crucial difference: the pump cycle is recursive. Each entity runs its own pump cycle internally, nested within the global pump cycle. Entities within entities, pumps within pumps. A2: fractal self-similarity across scale.")],
        spacing: { after: 240 }
      }),

      // Section 6: Field Mechanics
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("6. Field Mechanics (The Invisible Layer)")]
      }),
      new Paragraph({
        children: [new TextRun("The field is computed on a spatial grid. Resolution varies by distance to aperture.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Flow computation")]
      }),
      new Paragraph({
        children: [new TextRun("Each cell holds a flow vector (direction and magnitude) derived from Perlin noise, gravitational sources, wind patterns, or any combination. The flow evolves each frame according to the pump cycle.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("How field shapes boundary")]
      }),
      new Paragraph({
        children: [new TextRun("Over time, the flow vector at each cell influences nearby boundary objects. This is the core mechanic: the invisible shapes the visible.")]
      }),
      new Paragraph({
        children: [new TextRun("Mapping to natural processes: (1) Wind eroding terrain (flow = wind vectors, boundary = terrain mesh); (2) Water carving rivers (flow = water flow, boundary = ground geometry); (3) Gravity pulling objects (flow = gravitational field, boundary = object positions); (4) Culture shaping institutions (flow = social currents, boundary = organizational structure).")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Fractal Resonance Memory (from Xorzo FRT v3)")]
      }),
      new Paragraph({
        children: [new TextRun("The field does not just push; it remembers. Using SRL (Selective Rainbow Lock) mechanics from the Fractal Resonance Transformer:")]
      }),
      new Paragraph({
        children: [new TextRun("Carrier frequency adaptation: each field cell has a carrier frequency that drifts toward the dominant flow direction. Formula: carrier += carrier_lr × (1 - lock) × delta × T_mean.")]
      }),
      new Paragraph({
        children: [new TextRun("Lock deepening: when flow consistently resonates with a cell, its lock strength increases. Formula: lock_strength += lock_lr × T_mean × (1 - lock). This makes the cell resistant to future changes.")]
      }),
      new Paragraph({
        children: [new TextRun("Connection pruning: field connections that carry no traffic decay and eventually disappear. Use it or lose it.")]
      }),
      new Paragraph({
        children: [new TextRun("Trauma/freezing: sudden massive force locks a cell at maximum lock strength. It stops adapting entirely. Natural analog: earthquake reshaping terrain permanently.")]
      }),
      new Paragraph({
        children: [new TextRun("Dormant awakening: when persistent flow passes through regions with no active field cells, dormant cells awaken at the mean position of the unmatched flow. The field grows new structure where experience demands it.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("The Four-Stage Cascade (Thought to Identity)")]
      }),
      new Paragraph({
        children: [new TextRun("Field adaptation follows the same four stages as neural plasticity:")]
      }),
      new Paragraph({
        children: [new TextRun("1. Entertained: flow passes through a cell, barely affects it. A single rain drop on rock.")]
      }),
      new Paragraph({
        children: [new TextRun("2. Repeated: flow keeps passing through the same path. A groove forms. The cell's home position begins to migrate.")]
      }),
      new Paragraph({
        children: [new TextRun("3. Habituated: the groove is now a channel that attracts more flow toward itself. Self-reinforcing. The river does not need to discover the path; the path pulls the river.")]
      }),
      new Paragraph({
        children: [new TextRun("4. Identity: the Grand Canyon. The cell IS the accumulated history of flow. Its lock strength is near maximum. Removing it would be removing the terrain's identity.")],
        spacing: { after: 240 }
      }),

      // Page break before Section 7
      new Paragraph({ children: [new PageBreak()] }),

      // Section 7: Fracture and Fusion
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("7. Fracture and Fusion (E = 1 Redistribution)")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Fracture")]
      }),
      new Paragraph({
        children: [new TextRun("When an object's structural integrity drops below threshold (from excessive force, balance stress, or accumulated damage), it fractures. The parent's E = 1 redistributes across children via softmax.")]
      }),
      new Paragraph({
        children: [new TextRun("Process: generate N child energies (random raw values), softmax normalize them (sum = 1), each child inherits its share as initial energy, each child then normalizes internally to its own E = 1. This is A2: each fragment is a whole at its own scale.")],
        spacing: { after: 120 }
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Fusion")]
      }),
      new Paragraph({
        children: [new TextRun("When two objects are close enough, their frequencies match (cos-squared resonance > threshold), and both have high integrity, they merge. Conservation of momentum; carrier frequency becomes weighted average; the fused entity is a new circumpunct at a larger scale.")],
        spacing: { after: 240 }
      }),

      // Section 8: Balance Parameter
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("8. The Balance Parameter (Quality Dial)")]
      }),
      new Paragraph({
        children: [new TextRun("The balance parameter (the half-moon symbol, optimal at 0.5) is the universal quality control.")]
      }),
      new Paragraph({
        children: [new TextRun("Applied to entities: balance near 0.5 = healthy, full physics, full rendering. Balance drifting toward 0 or 1 = strained, simplified, eventually fractures.")]
      }),
      new Paragraph({
        children: [new TextRun("Applied to field regions: balance = ratio of convergent to emergent energy in the region. At 0.5, maximum entropy, richest dynamics. At extremes, the field is either over-structured (rigid, crystalline) or over-fluid (chaotic, noisy).")]
      }),
      new Paragraph({
        children: [new TextRun("Applied to the engine itself: the render/compute budget split. Too much render, not enough compute = pretty but dead (no field evolution). Too much compute, not enough render = alive but invisible (field is rich but nothing to see). Balance at 0.5 = the engine at its best.")]
      }),
      new Paragraph({
        children: [new TextRun("Fractal dimension at balance: D = 1 + balance = 1.5 (at balance = 0.5). This is the fractal dimension of Brownian motion, the coastline between structure and flow. The boundary between rendered objects and computed field is not a clean line; it is a 1.5D fractal coastline.")],
        spacing: { after: 240 }
      }),

      // Section 9: Multiplayer
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("9. Multiplayer Architecture (Session as Circumpunct)")]
      }),
      new Paragraph({
        children: [new TextRun("The multiplayer session is itself a circumpunct:")]
      }),
      new Paragraph({
        children: [new TextRun("Host = Aperture (soul of the session): The player with the lowest latency (best overall connection to the group) becomes the host. Lowest latency = strongest resonance = the natural convergence point through which all signals route.")]
      }),
      new Paragraph({
        children: [new TextRun("Mesh network = Field (Phi, mediating): Peer connections between all players. Shared state interpolation. The field between the circumpuncts.")]
      }),
      new Paragraph({
        children: [new TextRun("Session boundary = Body (who is in, who is out): The lobby, the matchmaking filter. The boundary that defines the session's identity.")]
      }),
      new Paragraph({
        children: [new TextRun("Host migration: When a player with better resonance joins (or the current host's connection degrades), the convergence point shifts. The session selects a new aperture. This is not a failure state; it is the pump cycle doing what it always does.")]
      }),
      new Paragraph({
        children: [new TextRun("Distributed foveation: Each client runs its own foveated compute/render budget based on its own camera position. The host arbitrates authoritative state for objects in overlapping foveated zones. Objects only one player can see: that player's client has authority. Objects multiple players can see: host arbitrates. Conflict resolution IS the boundary filtering.")],
        spacing: { after: 240 }
      }),

      // Section 10: 1.5D Coastline
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("10. The 1.5D Coastline")]
      }),
      new Paragraph({
        children: [new TextRun("Between flow and structure, between field and boundary, between the invisible and the visible, there is a fractal coastline at D = 1.5. This is the most important region in the engine.")]
      }),
      new Paragraph({
        children: [new TextRun("The coastline is where:")]
      }),
      new Paragraph({
        children: [new TextRun("• Erosion happens (flow meeting structure)")]
      }),
      new Paragraph({
        children: [new TextRun("• Cognition happens (experience meeting rules)")]
      }),
      new Paragraph({
        children: [new TextRun("• Gameplay happens (player input meeting world state)")]
      }),
      new Paragraph({
        children: [new TextRun("• Rendering meets physics (visible meets invisible)")]
      }),
      new Paragraph({
        children: [new TextRun("The engine should make this coastline feel alive. Where the field is actively shaping the boundary, particles should be denser, effects richer, sound more detailed. The coastline IS the game.")],
        spacing: { after: 240 }
      }),

      // Section 11: Scale Independence
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("11. Scale Independence (A2)")]
      }),
      new Paragraph({
        children: [new TextRun("The engine uses one pattern at every scale. There is no separate \"particle physics\" and \"rigid body physics\" and \"terrain physics.\" There is one circumpunct, one softmax, one pump cycle, applied recursively.")]
      }),
      new Paragraph({
        children: [new TextRun("Zoom in: sub-objects have their own field, their own pump cycle, their own E = 1.")]
      }),
      new Paragraph({
        children: [new TextRun("Zoom out: the entire scene is one circumpunct with its own field and boundary.")]
      }),
      new Paragraph({
        children: [new TextRun("Same code, different scale. Limited, not false.")]
      }),
      new Paragraph({
        children: [new TextRun("This means procedural generation is native. You do not need to store detail at every scale; you generate it on demand from the same rule. A2 guarantees consistency across scales because every scale uses the same pattern.")],
        spacing: { after: 240 }
      }),

      // Section 12: Summary of Core Equations
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("12. Summary of Core Equations")]
      }),

      // Equations table
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2340, 2340, 4680],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Equation", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Meaning", bold: true })], alignment: AlignmentType.CENTER })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Engine Use", bold: true })], alignment: AlignmentType.CENTER })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("E = 1")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Total energy is always one")] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Softmax normalization everywhere")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("softmax(v, T)")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Distributes budget across N items")] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Attention, render, compute, fracture")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("cos²(Δϕ / 2)")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Phase resonance between entities")] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Force modulation, fusion check, SRL")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("carrier += carrier_lr(1-lock)ΔT")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Adaptive frequency tracking")] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Field cell migration, home drift")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("lock += lock_lr T(1-lock)")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Lock deepening from resonance")] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Pathway strengthening, habituation")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("D = 1 + balance")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Fractal dimension at balance")] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Coastline complexity, LOD boundary")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("F = G m1 m2 / r²")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Convergence force")] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Gravity between circumpuncts")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Phi(t+dt) = emerge(rotate(converge(Phi(t))))")] })]
              }),
              new TableCell({
                borders,
                width: { size: 2340, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("The pump cycle")] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Every frame, entity, and scale")] })]
              })
            ]
          })
        ]
      }),

      new Paragraph({
        children: [new TextRun("")],
        spacing: { after: 400 }
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/sessions/wonderful-laughing-thompson/mnt/Fractal_Reality/Circumpunct_Game_Engine_Design_Spec.docx", buffer);
  console.log("Document created successfully!");
});
