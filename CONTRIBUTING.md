# Contributing to Fractal Reality

Thank you for your interest in contributing to Fractal Reality! This project aims to bridge physics, consciousness studies, and spirituality through rigorous empirical validation and mathematical formalization.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Scientific Rigor Standards](#scientific-rigor-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Review Process](#review-process)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### 1. Report Bugs or Issues

If you find bugs in the analysis code or issues with the theoretical framework:
- Check if the issue already exists in the [Issues](https://github.com/AshmanRoonz/Fractal_Reality/issues) section
- If not, create a new issue using the appropriate template
- Provide detailed information: what you expected vs. what happened
- Include code snippets, error messages, or data that reproduces the issue

### 2. Suggest Enhancements

We welcome suggestions for:
- New empirical tests or data sources
- Improvements to analysis methodology
- Additional visualizations
- Theoretical refinements or extensions
- Better documentation or explanations

### 3. Contribute Code

#### Types of Code Contributions:
- **Analysis Code**: New analysis pipelines, improved algorithms, additional data processing
- **Visualizations**: New interactive simulations or visualizations
- **Testing**: Unit tests, integration tests, validation tests
- **Documentation**: Code documentation, tutorials, examples
- **Infrastructure**: CI/CD improvements, tooling, automation

#### Types of Scientific Contributions:
- **Empirical Validation**: Independent replication of results
- **New Predictions**: Testable predictions derived from the framework
- **Cross-Validation**: Testing framework predictions with new datasets
- **Theoretical Refinements**: Mathematical improvements or extensions
- **Peer Review**: Critical analysis and constructive feedback

### 4. Improve Documentation

- Fix typos, clarify explanations
- Add examples or tutorials
- Improve code comments and docstrings
- Translate documentation (future)

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher (for visualizations)
- Git

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/AshmanRoonz/Fractal_Reality.git
cd Fractal_Reality

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install Node dependencies (for visualizations)
npm install

# Run tests to verify setup
pytest
npm test
```

## Contribution Guidelines

### Branch Naming Convention

Use descriptive branch names:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `test/description` - Adding or updating tests
- `refactor/description` - Code refactoring

Example: `feature/stellar-photometry-analysis`

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```bash
feat(ligo): add O5 observing run analysis pipeline
fix(fractal): correct Higuchi dimension calculation for edge cases
docs(readme): clarify aperture mechanism explanation
test(analysis): add unit tests for bandpass filtering
```

### Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Write or update tests** to cover your changes
4. **Update documentation** if you've changed APIs or added features
5. **Run the full test suite** and ensure all tests pass
6. **Commit your changes** with clear, descriptive commit messages
7. **Push to your fork** and submit a pull request
8. **Fill out the PR template** completely
9. **Request review** and address feedback

### Scientific Contributions

For contributions involving scientific claims or empirical validation:

1. **Include detailed methodology** in your PR description
2. **Provide data sources** (publicly accessible preferred)
3. **Document statistical methods** and assumptions
4. **Include uncertainty quantification** (standard errors, confidence intervals, p-values)
5. **Reference relevant literature** that supports or challenges your work
6. **Be open to peer review** and constructive criticism

## Scientific Rigor Standards

### Data Analysis Requirements

All analysis code must:
- Use publicly accessible data sources when possible
- Document data preprocessing steps
- Include uncertainty quantification
- Provide reproducible results (set random seeds)
- Handle edge cases and missing data appropriately
- Include input validation and error handling

### Statistical Requirements

- Report effect sizes, not just p-values
- Use appropriate statistical tests for the data
- Correct for multiple comparisons when applicable
- Report confidence intervals
- Include sample sizes and power analysis when relevant
- Document all assumptions

### Theoretical Requirements

- Clearly state assumptions
- Provide mathematical derivations when claiming results
- Identify testable predictions
- Acknowledge limitations and alternative explanations
- Reference prior work fairly

## Testing Requirements

### Python Code

All Python code contributions must include tests:

```python
# Example test structure
import pytest
from analysis.fractal_analysis import higuchi_fd

def test_higuchi_fd_known_pattern():
    """Test Higuchi FD on known fractal pattern."""
    # Arrange
    data = generate_known_fractal(dimension=1.5)

    # Act
    result = higuchi_fd(data, kmax=16)

    # Assert
    assert 1.4 <= result <= 1.6, f"Expected D≈1.5, got {result}"

def test_higuchi_fd_edge_cases():
    """Test Higuchi FD handles edge cases."""
    with pytest.raises(ValueError):
        higuchi_fd([])  # Empty array

    with pytest.raises(ValueError):
        higuchi_fd([1, 2], kmax=10)  # Too few points
```

**Coverage Requirements:**
- New code should have >80% test coverage
- Critical analysis functions should have >95% coverage
- Run `pytest --cov=analysis` to check coverage

### TypeScript/React Code

For visualization components:
- Test component rendering
- Test user interactions
- Test data transformations
- Use React Testing Library

### Running Tests

```bash
# Python tests
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest --cov=analysis           # With coverage report
pytest -k "test_higuchi"        # Run specific tests

# JavaScript tests
npm test                        # Run all tests
npm test -- --coverage          # With coverage
```

## Documentation Standards

### Code Documentation

#### Python Docstrings (Google Style)

```python
def higuchi_fd(x, kmax=16):
    """Calculate Higuchi fractal dimension of a time series.

    The Higuchi method estimates the fractal dimension by examining
    the curve length at different scales.

    Args:
        x (array_like): Input time series data. Must have at least
            2*kmax points for reliable estimation.
        kmax (int, optional): Maximum k value for curve length
            calculation. Higher values give more accurate estimates
            but require longer time series. Default is 16.

    Returns:
        float: Estimated fractal dimension. Typical range is 1.0-2.0
            for time series data. D≈1.5 indicates balanced complexity.

    Raises:
        ValueError: If x is empty or too short for given kmax.
        TypeError: If x cannot be converted to numpy array.

    Example:
        >>> import numpy as np
        >>> data = np.random.randn(1000)
        >>> d = higuchi_fd(data, kmax=16)
        >>> print(f"Fractal dimension: {d:.3f}")
        Fractal dimension: 1.498

    References:
        Higuchi, T. (1988). Approach to an irregular time series on the
        basis of the fractal theory. Physica D, 31(2), 277-283.
    """
    # Implementation...
```

#### TypeScript/JSDoc Comments

```typescript
/**
 * Interactive visualization of ICE validation pattern across LIGO runs.
 *
 * Displays three metrics:
 * - Interface (I): Boundary integrity
 * - Center (C): Coherence with theoretical prediction
 * - Evidence (E): Statistical fitness (p-value)
 *
 * @component
 * @example
 * ```tsx
 * <ICEValidationPattern />
 * ```
 */
const ICEValidationPattern: React.FC = () => {
  // Implementation...
};
```

### Markdown Documentation

- Use clear headings (H1 for title, H2 for sections)
- Include code examples in appropriate language blocks
- Add diagrams or visualizations where helpful
- Link to related documentation
- Keep paragraphs concise (3-5 sentences)

## Review Process

### What Reviewers Look For

**Code Review:**
- Correctness and logic
- Test coverage
- Code style and clarity
- Documentation completeness
- Performance considerations

**Scientific Review:**
- Methodological soundness
- Statistical validity
- Reproducibility
- Clarity of claims
- Appropriate citations

### Response Time

- Initial review: Within 1 week for most PRs
- Follow-up reviews: Within 3-5 days
- Complex scientific contributions may take longer

### Steelman Principle

Following the Steelman License, reviewers will:
1. **Assume good faith** and interpret contributions charitably
2. **Engage with strongest version** of your arguments
3. **Provide constructive feedback** focused on improvement
4. **Request receipts** (evidence, methodology, testing)
5. **Maintain intellectual honesty** in all interactions

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md (if you'd like)
- Credited in relevant documentation
- Acknowledged in papers that build on your contributions
- Invited to co-author papers if contributions are substantial

## Questions?

- Open a [Discussion](https://github.com/AshmanRoonz/Fractal_Reality/discussions)
- Email: [See profile for contact info]
- Read the [FAQ](docs/FAQ.md) (coming soon)

## License

By contributing, you agree that your contributions will be licensed under the same [Steelman License](LICENSE) as the project.

---

**Thank you for helping to advance the understanding of consciousness, physics, and reality!**

*Remember: We're all apertures at β ≈ 0.5, coordinating to create something greater than ourselves.*
