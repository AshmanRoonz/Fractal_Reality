# Contributing to Fractal Reality

Thank you for your interest in contributing! This project bridges physics, consciousness, and spirituality through rigorous empirical validation—demonstrating that mechanism and meaning are one continuous structure.

```
∇ → [ICE] → ℰ
Convergence → Validation → Emergence
```

Every contribution is an aperture operation creating eternal texture. Let's maintain β ≈ 0.5—the balance between rigor and creativity.

---

## Table of Contents

- [Foundation: [ICE] Ethics](#foundation-ice-ethics)
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Scientific Rigor Standards](#scientific-rigor-standards)
- [Steelman Review Process](#steelman-review-process)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Recognition and Sacred Reciprocity](#recognition-and-sacred-reciprocity)

---

## Foundation: [ICE] Ethics

All contributions must validate through the three-fold check:

### **Interface: Respect All Boundaries**

- Honor others' autonomy and sovereignty (all •' operators are equal)
- Practice consent in collaboration
- Respect licenses and attribution
- Maintain professional boundaries
- No harassment or boundary violations

**Code level:** Follow APIs, respect dependencies, don't break interfaces  
**Human level:** Respect people's time, expertise, and contributions

### **Center: Be Authentic AND Aligned**

**Authenticity (•'):**
- Express your genuine understanding
- Don't pretend expertise you lack
- Share your actual reasoning
- Acknowledge your uncertainty

**Alignment (•):**
- Ground in truth and evidence
- Follow logic where it leads
- Correct mistakes when found
- Serve reality over ego

**Code level:** Write honest code that does what it claims  
**Scientific level:** Report results truthfully, including negative results

### **Evidence: Ground in Reality Always**

- Make falsifiable claims
- Provide reproducible methods
- Include data and sources
- Quantify uncertainty
- Let reality judge

**Code level:** Include tests that verify behavior  
**Scientific level:** Make testable predictions, show your work

---

## Code of Conduct

**Read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.**

Key principles:
- **Steelman by default** (find strongest version before critiquing)
- **Soul equality** (all •' = ∞, judge ideas by evidence not authority)
- **Sacred reciprocity** (support others' validation to strengthen the field)
- **Eternal consequences** (your contributions build permanent texture)
- **Balance at β ≈ 0.5** (rigor + creativity, structure + openness)

---

## How Can I Contribute?

### 1. Report Issues (Interface Validation)

**Found a bug or theoretical inconsistency?**

- Check existing [Issues](https://github.com/AshmanRoonz/Fractal_Reality/issues)
- Create new issue with template
- Provide [ICE] evidence:
  - **Interface:** What boundary broke? (expected vs actual)
  - **Center:** What's the core problem? (strip to essence)
  - **Evidence:** How to reproduce? (data, code, steps)

**Good issue:**
> "Higuchi FD calculation gives D=2.3 for white noise (expected D≈2.0). Reproduced with np.random.randn(1000), kmax=16. See attached code. Possible issue in L_k calculation line 47."

**Poor issue:**
> "The fractal thing doesn't work. Please fix."

### 2. Suggest Enhancements (Emergent Contribution)

We welcome suggestions for:

**Empirical:**
- New data sources for validation
- Additional analysis methods
- Better statistical approaches
- Cross-validation with other datasets

**Theoretical:**
- Mathematical refinements
- New predictions from framework
- Alternative derivations
- Falsification tests

**Practical:**
- Improved visualizations
- Better documentation
- Tutorial development
- Educational materials

**For each suggestion:**
1. Steelman the current approach (what's it doing right?)
2. Identify specific limitation (evidence-based)
3. Propose improvement (with reasoning)
4. Consider falsification (how to test if it's better?)

### 3. Contribute Code (Validated Pattern)

#### Code Contribution Types:

**Analysis Pipelines:**
- New data processing workflows
- Statistical analysis improvements
- Algorithm optimizations
- Validation methodology

**Visualizations:**
- Interactive simulations
- Data visualization improvements
- Educational animations
- Research graphics

**Testing:**
- Unit tests (validate components)
- Integration tests (validate combinations)
- Property tests (validate mathematical requirements)
- Empirical validation (validate predictions)

**Infrastructure:**
- CI/CD improvements
- Build system optimization
- Development tooling
- Documentation generators

### 4. Contribute Science (Validated Knowledge)

**Independent Replication:**
- Reproduce published results
- Test on new datasets
- Cross-validate predictions
- Document methodology

**New Predictions:**
- Derive testable consequences
- Identify observation protocols
- Quantify expected effects
- Specify falsification criteria

**Critical Analysis:**
- Identify assumptions
- Find alternative explanations
- Propose stronger tests
- Steelman then critique

**Theoretical Extensions:**
- Mathematical generalizations
- New applications
- Interdisciplinary connections
- Formalization improvements

### 5. Improve Documentation (Texture Transmission)

- Fix errors and clarify explanations
- Add examples and tutorials
- Improve code documentation
- Create learning pathways
- Translate content (future)

---

## Development Setup

### Prerequisites

- Python 3.9+ (analysis)
- Node.js 16+ (visualizations)
- Git
- Optional: LaTeX (for paper generation)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/AshmanRoonz/Fractal_Reality.git
cd Fractal_Reality

# Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Node dependencies
npm install

# Verify setup ([ICE] check)
pytest                    # Interface: tests pass
npm test                  # Center: code coherent
python verify_setup.py    # Evidence: environment valid
```

---

## Contribution Guidelines

### Branch Naming (Organized Texture)

Use descriptive names indicating purpose:

- `feature/description` - New functionality
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `test/description` - Testing improvements
- `refactor/description` - Code restructuring
- `validation/description` - Empirical validation work

**Examples:**
- `feature/o5-ligo-analysis`
- `fix/higuchi-edge-cases`
- `validation/bubble-chamber-data`
- `docs/layer-9-clarification`

### Commit Convention (Validated Changes)

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body explaining the validation]

[optional footer with references]
```

**Types:**
- `feat`: New feature (emergent)
- `fix`: Bug fix (interface repair)
- `docs`: Documentation (texture transmission)
- `test`: Testing (validation improvement)
- `refactor`: Restructuring (center coherence)
- `perf`: Performance (efficiency optimization)
- `validate`: Empirical validation (evidence grounding)
- `derive`: Theoretical derivation (mathematical extension)

**Examples:**

```bash
feat(ligo): add O5 run analysis with corrected calibration

Implements analysis pipeline for LIGO O5 observing run.
Includes Higuchi FD calculation with improved edge handling.
Validates against framework prediction D≈1.5 (p=0.951).

Refs: #42, analysis/tests/ligo/O5_README.md

---

fix(fractal): handle edge case in Higuchi FD for short series

Previously crashed with N < 2*kmax. Now validates input and
provides helpful error message with minimum length requirement.

Closes #89

---

validate(bubble): add bubble chamber particle track analysis

Cross-validates D≈1.5 prediction using 33 particle tracks
from bubble chamber data. Results: D=1.503±0.040 (consistent).

See analysis/tests/bubble_chamber/README.md for methodology.

---

docs(layer-9): clarify soul equality mathematical foundation

Added explicit derivation showing ∞ = ∞ (operator equality)
vs. manifestation differences. Addresses FAQ #15.
```

### Pull Request Process (Aperture Operation)

Your PR is an aperture operation—it must validate at interfaces:

#### **1. Prepare ([ICE] Pre-check)**

- Fork repository, branch from `main`
- Make focused changes (one purpose per PR)
- Write/update tests (validate behavior)
- Update documentation (maintain coherence)
- Run full test suite (verify integration)
- Check [ICE] locally:
  - **Interface:** Does it break existing APIs?
  - **Center:** Is the code authentic and aligned?
  - **Evidence:** Do tests validate claims?

#### **2. Submit (Create Validated Pattern)**

- Push to your fork
- Open PR with complete template
- Title: `<type>(<scope>): <clear description>`
- Description must include:
  - **What:** Changes made
  - **Why:** Motivation and reasoning
  - **How:** Implementation approach
  - **Validation:** Tests and evidence
  - **[ICE] Check:** How it validates

#### **3. Review (Collaborative Validation)**

**Expect steelman review:**
- Reviewers will find strongest version of your contribution
- Feedback aims to improve, not reject
- Questions seek understanding, not gotchas
- Criticism addresses code/ideas, not you

**Your role during review:**
- Respond promptfully (within ~1 week)
- Address feedback substantively
- Update based on validation requirements
- Maintain [ICE] throughout iteration

#### **4. Merge (Eternal Texture)**

Once validated:
- Squash commits or keep history (maintainer decides)
- Merged to `main` branch
- Automatically deployed (if applicable)
- **Your contribution becomes eternal texture**

---

## Scientific Rigor Standards

### Data Analysis Requirements (Evidence Ethics)

All analysis code must:

**Reproducibility:**
- Use publicly accessible data when possible
- Document data sources and versions
- Set random seeds for stochastic processes
- Include environment specifications
- Provide complete pipeline (raw data → results)

**Transparency:**
- Document all preprocessing steps
- Show intermediate results
- Report negative findings
- Include failed approaches (if informative)
- Acknowledge limitations explicitly

**Validation:**
- Include uncertainty quantification (SEM, CI, p-values)
- Handle missing data appropriately
- Validate edge cases and boundary conditions
- Test against known patterns
- Cross-validate when possible

**Code Quality:**
- Input validation and error handling
- Sensible defaults with clear documentation
- Efficient algorithms (avoid O(n³) when O(n log n) exists)
- Clear variable names (avoid single letters except i, j, k in loops)
- Modular design (functions do one thing well)

### Statistical Requirements (Evidence Grounding)

**Report effect sizes, not just p-values:**
```python
# Good
print(f"D = {mean_d:.3f} ± {sem:.3f}")
print(f"Framework prediction: D ≈ 1.5")
print(f"Difference: {abs(mean_d - 1.5):.3f}")
print(f"Statistical test: t = {t_stat:.2f}, p = {p_value:.3f}")

# Insufficient
print(f"p = {p_value}")  # Effect size unknown!
```

**Use appropriate tests:**
- Normal data → t-test or ANOVA
- Non-normal → Mann-Whitney or Kruskal-Wallis
- Multiple comparisons → Bonferroni or FDR correction
- Time series → account for autocorrelation
- Always check assumptions!

**Report confidence intervals:**
```python
# Calculate 95% CI
ci_lower = mean - 1.96 * sem
ci_upper = mean + 1.96 * sem
print(f"95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]")
```

**Include sample size and power:**
- Report N for all analyses
- For null results, include power analysis
- Justify sample sizes (a priori power ≥ 0.8)

### Theoretical Requirements (Center Coherence)

**State assumptions explicitly:**
- Mathematical assumptions (linearity, independence, etc.)
- Physical assumptions (scales, regimes, approximations)
- Philosophical assumptions (realism, causality, etc.)

**Provide derivations:**
- Show mathematical steps for claimed results
- Don't skip "obvious" steps (obvious to whom?)
- Include dimensional analysis
- Check limiting cases

**Identify predictions:**
- What does this predict that's testable?
- What observation would falsify it?
- How precise are the predictions?
- What's the expected effect size?

**Acknowledge alternatives:**
- What other explanations exist?
- How do we distinguish them empirically?
- What evidence would favor alternatives?
- Be intellectually honest about limitations

---

## Steelman Review Process

### The Steelman Principle in Action

**Reviewers commit to:**

1. **Understand fully** before critiquing
   - Ask clarifying questions
   - Verify understanding ("Am I correct that you mean...")
   - Explore motivation and reasoning

2. **Find strongest version** of contribution
   - Identify what works well
   - Strengthen weak points if possible
   - Suggest improvements constructively

3. **Engage substantively** with core ideas
   - Address central claims, not peripheral issues
   - Provide specific, actionable feedback
   - Back criticisms with evidence and reasoning

4. **Build together** toward better science
   - Collaborative refinement, not adversarial debate
   - Celebrate insights and progress
   - Acknowledge when contributor is right

5. **Maintain [ICE] validation** throughout
   - **Interface:** Respect contributor's autonomy
   - **Center:** Stay honest and authentic
   - **Evidence:** Ground feedback in reality

### What Reviewers Look For

**Interface Validation (Does it integrate well?):**
- Consistent with existing APIs
- Doesn't break current functionality
- Clear interfaces and contracts
- Appropriate error handling
- Good separation of concerns

**Center Validation (Is it coherent and aligned?):**
- Code does what it claims
- Logic is sound and clear
- Aligns with project principles
- Authentic implementation (no cargo-culting)
- Internally consistent

**Evidence Validation (Is it grounded in reality?):**
- Tests validate behavior
- Claims backed by evidence
- Results reproducible
- Statistical methods appropriate
- Predictions falsifiable

### Example Reviews

**❌ Strawman Review (Violates all three ethics):**
> "This analysis is wrong. You obviously don't understand fractal dimension. The code is messy and the results are meaningless. Did you even read the literature?"

*Interface violation:* Attacks person, not idea  
*Center violation:* Dismissive, not constructive  
*Evidence violation:* No specific evidence provided

**✓ Steelman Review (Maintains [ICE]):**
> "Thanks for this contribution! The core insight about using Higuchi FD is solid. I have some suggestions to strengthen the analysis:
>
> 1. **Statistical concern:** With N=20, power is ~0.45 for detecting D=1.5 vs D=1.3. Consider increasing sample size or reporting power explicitly. See power_analysis.py for calculations.
>
> 2. **Edge case:** Line 47 crashes when len(data) < 2*kmax. Suggest adding input validation: `if len(data) < 2*kmax: raise ValueError(...)`
>
> 3. **Reproducibility:** Consider setting np.random.seed() for consistency across runs.
>
> 4. **Documentation:** Could you add a docstring explaining what k_max parameter controls? Not obvious to readers unfamiliar with Higuchi method.
>
> The overall approach is sound and validates D≈1.5 well. These refinements would make it even stronger. Happy to discuss any of these points!"

*Interface respect:* Honors contributor's work  
*Center alignment:* Specific, constructive, honest  
*Evidence grounding:* Provides concrete suggestions with reasoning

### Response Expectations

**Timeline:**
- Initial review: Within 7 days (most PRs)
- Follow-up: Within 3-5 days
- Complex scientific contributions: Up to 2 weeks
- If delayed, maintainer will communicate

**Your response:**
- Address feedback within ~1-2 weeks
- Respond to all substantive points
- Update PR or explain reasoning
- Ask clarifying questions if needed
- Maintain [ICE] in responses

---

## Testing Requirements

### Testing Philosophy

**Tests validate that code does what it claims.**

Every function makes implicit promises:
- "I calculate Higuchi FD correctly"
- "I handle edge cases gracefully"
- "I return results in specified format"

Tests check these promises against reality.

### Python Testing

**Structure:**
```python
# tests/test_fractal_analysis.py
import pytest
import numpy as np
from analysis.fractal_analysis import higuchi_fd

class TestHiguchiFD:
    """Test suite for Higuchi fractal dimension calculation."""
    
    def test_known_fractal_pattern(self):
        """Validates D≈1.5 for generated fractal."""
        # Arrange: Create known fractal with D=1.5
        data = generate_fbm(n=2000, hurst=0.5)  # H=0.5 → D=1.5
        
        # Act: Calculate dimension
        d = higuchi_fd(data, kmax=16)
        
        # Assert: Check within expected range
        assert 1.4 <= d <= 1.6, f"Expected D≈1.5, got {d:.3f}"
    
    def test_white_noise_dimension(self):
        """White noise should have D≈2.0 (maximum complexity)."""
        data = np.random.randn(1000)
        d = higuchi_fd(data, kmax=16)
        assert 1.8 <= d <= 2.2, f"Expected D≈2.0 for white noise, got {d:.3f}"
    
    def test_input_validation(self):
        """Should raise ValueError for invalid inputs."""
        with pytest.raises(ValueError, match="too short"):
            higuchi_fd([1, 2, 3], kmax=10)
        
        with pytest.raises(ValueError, match="empty"):
            higuchi_fd([], kmax=10)
    
    def test_deterministic_output(self):
        """Same input should give same output."""
        data = np.random.randn(500)
        d1 = higuchi_fd(data, kmax=16)
        d2 = higuchi_fd(data, kmax=16)
        assert d1 == d2, "Results should be deterministic"
    
    @pytest.mark.parametrize("kmax", [4, 8, 16, 32])
    def test_various_kmax(self, kmax):
        """Should work with various k_max values."""
        data = np.random.randn(1000)
        d = higuchi_fd(data, kmax=kmax)
        assert 1.0 <= d <= 2.0, f"Unrealistic dimension {d:.3f}"
```

**Coverage Requirements:**
- New code: ≥80% coverage
- Critical analysis functions: ≥95% coverage
- Run: `pytest --cov=analysis --cov-report=html`

### React/TypeScript Testing

```typescript
// tests/components/ICEVisualization.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ICEVisualization } from '../components/ICEVisualization';

describe('ICEVisualization', () => {
  it('renders three validation metrics', () => {
    render(<ICEVisualization data={mockData} />);
    
    expect(screen.getByText(/Interface/i)).toBeInTheDocument();
    expect(screen.getByText(/Center/i)).toBeInTheDocument();
    expect(screen.getByText(/Evidence/i)).toBeInTheDocument();
  });
  
  it('updates visualization on data change', () => {
    const { rerender } = render(<ICEVisualization data={data1} />);
    expect(screen.getByText(/D = 1.50/)).toBeInTheDocument();
    
    rerender(<ICEVisualization data={data2} />);
    expect(screen.getByText(/D = 1.63/)).toBeInTheDocument();
  });
});
```

### Running Tests

```bash
# Python: Run all tests
pytest

# Python: Verbose with coverage
pytest -v --cov=analysis --cov-report=term-missing

# Python: Specific test file
pytest tests/test_fractal_analysis.py

# Python: Specific test
pytest tests/test_fractal_analysis.py::TestHiguchiFD::test_known_fractal_pattern

# JavaScript: All tests
npm test

# JavaScript: With coverage
npm test -- --coverage

# JavaScript: Watch mode (during development)
npm test -- --watch
```

---

## Documentation Standards

### Python Docstrings (Google Style + [ICE])

```python
def validate_ice_pattern(data, prediction=1.5, alpha=0.05):
    """Validate data against [ICE] framework prediction.
    
    Performs three-fold validation:
    - Interface: Checks data integrity and format
    - Center: Tests coherence with theoretical prediction
    - Evidence: Grounds with statistical significance testing
    
    Args:
        data (array_like): Observed fractal dimension values.
            Should be 1D array of floats. Typically from
            Higuchi FD or similar fractal analysis.
        prediction (float, optional): Theoretical prediction
            to test against. Default is 1.5 (framework prediction
            for worldlines). Must be in range [1.0, 2.0].
        alpha (float, optional): Significance level for
            hypothesis testing. Default is 0.05 (95% confidence).
            Must be in range (0, 1).
    
    Returns:
        dict: Validation results with keys:
            - 'interface_valid' (bool): Data format check passed
            - 'center_coherent' (bool): Within prediction range
            - 'evidence_grounded' (bool): Statistically significant
            - 'mean_d' (float): Mean fractal dimension
            - 'sem' (float): Standard error of mean
            - 'p_value' (float): Two-tailed t-test p-value
            - 'consistent' (bool): All three checks passed
    
    Raises:
        ValueError: If data is empty, contains NaN/Inf, or
            prediction/alpha out of valid range.
        TypeError: If inputs cannot be converted to appropriate types.
    
    Example:
        >>> data = [1.48, 1.52, 1.50, 1.49, 1.51]
        >>> result = validate_ice_pattern(data, prediction=1.5)
        >>> print(f"Consistent: {result['consistent']}")
        Consistent: True
        >>> print(f"p-value: {result['p_value']:.3f}")
        p-value: 0.856
    
    Note:
        This implements the [ICE] validation structure from Layer 5.
        All three checks (Interface, Center, Evidence) must pass
        for full validation. Partial validation possible if some
        checks pass but not all.
    
    References:
        See Layer 5 (Validation) and Layer 6 (Mathematics) for
        theoretical foundation of [ICE] validation requirements.
    """
    # Implementation...
```

### Markdown Documentation (Layered Understanding)

**Structure for clarity:**

```markdown
# Feature Name

> Brief one-sentence description

## Quick Start (Layer 0)

Minimum viable example:

```python
from analysis import higuchi_fd
d = higuchi_fd(data)
print(f"Dimension: {d:.3f}")
```

## Concept (Layer 1)

What is fractal dimension? Why does it matter?

[Accessible explanation without jargon]

## Usage (Layer 2)

Detailed usage with all parameters:

```python
result = higuchi_fd(
    data,
    kmax=16,           # Maximum scale
    normalize=True,    # Normalize to [0,1]
    return_all=False   # Return only D
)
```

## Theory (Layer 3)

Mathematical foundation...

[For those who want depth]

## Examples (Layer 4)

Real-world applications...

## Troubleshooting (Layer 5)

Common issues and solutions...
```

**Fractal documentation principle:**
Each layer contains the whole, but at increasing resolution.
Reader stops when they have enough detail.

---

## Recognition and Sacred Reciprocity

### How We Honor Contributors

**All contributors receive:**

1. **Attribution** in CONTRIBUTORS.md (if desired)
2. **Credit** in relevant documentation
3. **Acknowledgment** in papers building on work
4. **Co-authorship** if contribution substantial

### What Counts as "Substantial"?

**Code contributions:**
- Major feature implementation
- Significant algorithm improvements
- Critical bug fixes enabling validation
- Extensive testing infrastructure

**Scientific contributions:**
- Independent validation of predictions
- New empirical tests or data sources
- Theoretical extensions or derivations
- Peer review improving quality

**Documentation contributions:**
- Comprehensive tutorials or guides
- Significant clarity improvements
- Educational materials enabling understanding

### Sacred Reciprocity Principle

**Supporting others' validation strengthens the field you exist in.**

When you contribute:
- You enable others' work (texture transmission)
- You strengthen collective validation (field improvement)
- You create eternal patterns (permanent contribution)
- You participate in coordinated emergence (β ≈ 0.5)

**This isn't altruism—it's structural intelligence.**

---

## Questions and Support

### Getting Help

**Before asking:**
1. Read relevant documentation (Layers 0-12)
2. Search existing issues and discussions
3. Check FAQ (coming soon)

**When asking:**
1. Provide [ICE] context:
   - **Interface:** What are you trying to do?
   - **Center:** What's the core question?
   - **Evidence:** What have you tried?
2. Include minimal reproducible example
3. Show error messages or unexpected behavior
4. Specify environment (OS, Python version, etc.)

**Where to ask:**
- **Questions:** [Discussions](https://github.com/AshmanRoonz/Fractal_Reality/discussions)
- **Bugs:** [Issues](https://github.com/AshmanRoonz/Fractal_Reality/issues)
- **Email:** See profile for contact info

### Communication Channels

**GitHub Discussions:**
- General questions
- Theoretical discussions
- Feature proposals
- Community interaction

**GitHub Issues:**
- Bug reports
- Specific problems
- Tracked action items

**Email:**
- Private concerns
- Collaboration proposals
- Sensitive topics

---

## License

By contributing, you agree your contributions will be licensed under the [Steelman License](LICENSE).

**What this means:**
- Maximum openness for scientific validation
- Attribution required (honor contributions)
- Commercial use allowed (with attribution)
- Modifications allowed (enabling evolution)
- No warranty (standard open source)

---

## Final Words

```
∞ ↔ •
```

**You are an eternal •' operator organizing temporary ∞.**

Every contribution creates texture that persists forever. Every line of code, every insight, every validation—permanent geometric structure in ∞'.

**We're coordinating at β ≈ 0.5:**
- Not too rigid (convergent ∇)
- Not too chaotic (emergent ℰ)
- Perfect balance (creative yet structured)

**Maintain [ICE] in all contributions:**
- **Interface:** Respect boundaries
- **Center:** Stay authentic and aligned
- **Evidence:** Ground in reality

**Thank you for helping demonstrate that mechanism and meaning are one.**

---

*Remember: We are all apertures at β ≈ 0.5, coordinating to create something greater than ourselves.*

*Your choices build eternal texture. Choose wisely.*

**Version 2.0 — October 2025**  
*Based on Fractal Reality ethics and Steelman principles*
