# Steelman License FAQ

**Frequently Asked Questions about the Steelman License (SML-P-2.0)**

---

## General Questions

### What is the Steelman License?

The Steelman License is a **permissive open-source license** that combines the freedom of MIT/Apache licenses with requirements for intellectual honesty and reproducibility.

**Key principle:** "Steelman first, receipts always."

**You can:** Use commercially, modify, distribute, deploy freely  
**You must:** Keep attribution, document changes honestly, enable verification

### Why create a new license instead of using MIT or Apache?

Traditional permissive licenses don't address:
- Misrepresentation of results
- Undocumented modifications
- Irreproducible claims
- Intellectual dishonesty

The Steelman License adds **accountability** while maintaining **freedom**.

It's for projects where **scientific integrity** and **reproducibility** matter as much as code freedom.

### Is this OSI-approved?

Not yet. The Steelman License is novel (created 2025) and hasn't been submitted to the Open Source Initiative for approval.

However, it meets the **Open Source Definition** criteria:
- ✓ Free redistribution
- ✓ Source code availability
- ✓ Derived works allowed
- ✓ No discrimination against persons/groups/fields
- ✓ Rights apply to all recipients
- ✓ License must not be specific to a product
- ✓ License must not restrict other software
- ✓ License must be technology-neutral

The novel elements (receipts requirement, right to participate) don't violate OSI principles but add accountability.

### What projects should use this license?

**Ideal for:**
- Scientific software (where reproducibility is critical)
- AI/ML models (where training details matter)
- Data analysis pipelines (where methodology must be transparent)
- Frameworks making testable predictions (where honesty about modifications matters)
- Research tools (where misrepresentation harms science)

**Also good for:**
- Any project valuing intellectual honesty
- Communities emphasizing steelman discourse
- Projects from outsider researchers (protects against misrepresentation)

**Maybe not ideal for:**
- Simple utility libraries (overkill for low-stakes code)
- Projects needing corporate adoption above all (unfamiliar license may deter)
- Rapid prototyping projects (receipts overhead may slow things down)

### How does it compare to other licenses?

| Feature | MIT/BSD | Apache 2.0 | GPL v3 | Steelman |
|---------|---------|------------|--------|----------|
| **Permissive** | ✓ | ✓ | ✗ | ✓ |
| **Commercial use** | ✓ | ✓ | ✓ | ✓ |
| **Copyleft** | ✗ | ✗ | ✓ | ✗ |
| **Patent grant** | ✗ | ✓ | ✓ | ✓ |
| **Attribution** | ✓ | ✓ | ✓ | ✓ |
| **Anti-misrepresentation** | ✗ | ✗ | ✗ | ✓ |
| **Receipts required** | ✗ | ✗ | ✗ | ✓ |
| **Reproducibility** | ✗ | ✗ | ✗ | ✓ |
| **Right to participate** | ✗ | ✗ | ✗ | ✓ |

**Summary:** As permissive as MIT/Apache, but with intellectual honesty requirements.

---

## Receipts Requirements

### What exactly are "receipts"?

A plain-text or markdown file documenting your modifications, including:

1. **Changes:** What you added/removed/modified
2. **Evidence:** How you tested (or explicit statement you didn't)
3. **Versioning:** Version/date/commit hash/contact
4. **Rollback:** How to revert to upstream
5. **Scale:** Scope of changes (lines, files, components)
6. **Known Issues:** Bugs or limitations introduced

See **Appendix B** of the license for a complete template.

### When do I need to provide receipts?

**Only when you distribute or deploy a modified version.**

- ✓ Publishing modified code on GitHub
- ✓ Deploying modified version as a service
- ✓ Distributing modified binaries
- ✓ Publishing a paper using modified code
- ✗ Using internally (no distribution)
- ✗ Contributing to upstream (upstream handles it)
- ✗ Just using unmodified code

### Do receipts need to be in a specific format?

No specific format required, but must be:
- Plain text or markdown (human-readable)
- Include all required fields (§0 definition)
- Accessible (included in distribution or clearly linked)

**Recommended:** Use the template in Appendix B of the license.

### What if I didn't test my modifications?

**Be honest about it.**

From §2.2: "Description of testing/evaluation performed... OR an explicit statement that no testing was performed."

**Example:**
```markdown
## Evidence of Testing
**Testing performed:** No

**Reason:** These are experimental modifications for personal use. 
They have not been validated against the framework's predictions 
or tested for correctness. Use at your own risk.
```

**Honesty is the requirement, not perfection.**

### How detailed do receipts need to be?

**Sufficient for independent verification and reproduction.**

**Too vague:** ❌
```
## Changes
- Made it better
- Fixed some stuff
- Updated algorithms
```

**Sufficient:** ✓
```
## Changes
- Modified Higuchi FD calculation in src/fractal.py lines 47-89
- Changed k_max default from 16 to 32 for improved accuracy
- Added GPU acceleration using cupy (new dependency)
- Approximately 200 lines modified across 3 files (~5% of codebase)

## Evidence of Testing
- Tested on synthetic fractals: D=1.5±0.02 (N=100 trials)
- Validated against LIGO O4 data: matches upstream within 2%
- GPU version 10x faster on 10K+ point series
- See tests/validation_report.md for full results
```

### Can I use a changelog as receipts?

**Yes, if it meets the requirements.**

A well-maintained `CHANGELOG.md` that includes testing evidence, versioning, and rollback instructions can serve as receipts.

**Most changelogs lack:** Testing evidence, known issues, rollback instructions.

**Solution:** Either enhance your changelog or create separate `RECEIPTS.md`.

---

## Right to Participate

### What does "right to participate" mean?

The original author (Ashman Roonz) retains the right to be invited to participate in derivative works.

**This is satisfied by:** Sending a timely invitation (within 30 days)

**This does NOT grant:**
- Veto power over your project
- Required co-authorship
- Ownership of your modifications
- Control over your decisions

### Why does this clause exist?

**Theoretical reason:** Original operator (•') maintains connection to derivative operators (fractal self-similarity)

**Practical reason:** Prevents complete appropriation without engagement

**Ethical reason:** If you're building something significant with someone's work, they should at least know about it

### Do I need to accept contributions from the original author?

**No.** 

Sending the invitation satisfies §2.01, regardless of whether participation is accepted or contributions merged.

You maintain full control over your project.

### What counts as a "timely invitation"?

**Within 30 days of:**
- Initial public release (open-source)
- Commercial launch (products/services)
- Publication (academic papers using the work)

**Does not apply to:** Private/internal use unless later distributed.

### What should the invitation include?

**Minimum:**
- Notice that you're creating a derivative work
- Brief description of the project
- Invitation to participate (as advisor, contributor, or community member)
- Contact information
- Acknowledgment this satisfies §2.01

See examples in NOTICE.md.

### What if I can't find contact information?

**Good faith effort is sufficient:**

1. Check the repository's README, CONTRIBUTORS, AUTHORS files
2. Check the commit history for author email
3. Open a GitHub issue in the upstream repository
4. Post in project discussions or forums
5. Document your attempts

If you make a reasonable effort and can't locate the author, you've satisfied the requirement in good faith.

### Does this apply to forks?

**Depends on the fork's purpose:**

- **Contributing back upstream:** No invitation needed (that's the point of forks)
- **Personal experimentation:** No invitation needed (not distributed)
- **Significant independent development:** Yes, if distributed/deployed
- **Commercial product:** Yes, always

**Rule of thumb:** If it becomes a separate project with its own identity, send an invitation.

---

## Compliance Questions

### I'm using this for my PhD research. Do I need receipts?

**If you're modifying the code and publishing results: Yes.**

Academic papers using modified code should include:
- Receipts in supplementary materials
- Methodology section describing modifications
- Link to code repository with receipts
- Clear distinction between upstream and modified results

This is good scientific practice anyway!

### I made a tiny bug fix. Do I need full receipts?

**Yes, but they can be proportionally brief.**

**Example for minor fix:**
```markdown
# Receipts for Bug Fix Release

## Changes
Fixed off-by-one error in src/fractal.py line 47 (1 line changed)

## Evidence
Added unit test demonstrating fix in tests/test_fractal.py
All 127 tests pass

## Versioning
v1.0.1 - 2025-10-23 - bugfix@example.com

## Rollback
git checkout v1.0.0

## Known Issues
None introduced
```

**2 minutes to write, satisfies requirement.**

### Can I bundle this in a larger product?

**Yes, with conditions:**

If your product includes this Work as a component:
- Include LICENSE file in distribution
- Provide attribution in about/credits
- If you modified it, include receipts
- Send participation invitation (for commercial products)

You don't need to open-source your entire product (not copyleft).

### What if I'm using this in proprietary software?

**Totally fine.** This is a permissive license.

**You must:**
- Include attribution
- If you modified it, provide receipts
- Send participation invitation
- Meet other §2 conditions

**You don't have to:**
- Open-source your code
- Share your proprietary components
- Release your modifications (though encouraged)

### Do I need receipts for configuration changes?

**Yes, if distributed.**

Configuration changes can significantly affect behavior. Document:
- Which parameters changed
- Why you changed them
- How you tested the new configuration
- Expected behavior differences

### What about translations or documentation changes?

**Depends on scope:**

**Minor fixes:** Brief receipts sufficient
**Complete translation:** Document which files translated, by whom, any cultural adaptations
**Major doc rewrite:** Note what changed, why, what's your interpretation vs. upstream

### I forked on GitHub but haven't changed anything. Do I need receipts?

**No.** Just forking doesn't require receipts.

Receipts are only needed when you:
- Distribute a modified version, OR
- Deploy a modified version as a service

A fork sitting on GitHub that's clearly a fork (with GitHub's fork marker) doesn't trigger requirements.

---

## Technical Questions

### Is this GPL-compatible?

**No, it's not copyleft.**

You can't relicense Steelman-licensed code as GPL because GPL requires derivative works to also be GPL.

**But:** You can use Steelman-licensed code in a GPL project as a separate component (like using an MIT-licensed library in a GPL program).

### Can I relicense my modifications?

**Yes, your modifications only** (§6).

You can license your original contributions under additional or different terms, provided:
- You don't restrict recipients' rights to the unmodified upstream portions
- Your terms are clearly separated from the Steelman License
- All Steelman License conditions still apply to the upstream portions

**Example:** Add a commercial license option for your modifications while keeping upstream under Steelman.

### What happens if the license is violated?

**Automatic termination** (§9), but with cure period:

1. **Discovery:** You or someone else discovers a violation
2. **Grace period:** 30 days to cure the violation
3. **Cure:** If fixed within 30 days, license automatically restored
4. **Failure to cure:** License terminated permanently (unless reinstated by copyright holder)

**Downstream recipients:** Not affected if they received the Work in compliance.

### Can I use this with other licenses in the same project?

**Yes, if they're compatible.**

**Compatible (can combine):**
- MIT
- BSD
- Apache 2.0
- Other permissive licenses

**Incompatible (can't combine in derived work):**
- GPL (copyleft conflict)
- Proprietary licenses with no distribution rights
- Licenses prohibiting modification

**You can:** Use Steelman-licensed components in a larger multi-licensed project.

### What's the patent grant?

From §1: "Non-assertion covenant from each contributor covering their contributor-owned patents necessarily infringed by their contributions."

**Translation:** Contributors promise not to sue you for patent infringement for patents they own that are necessarily used by their contributions.

**Similar to:** Apache 2.0 patent grant

### Does this license have a "license compatibility" clause?

**Yes, implicitly through §6 and §11.**

- §6: You can relicense your modifications under additional terms (provided they don't restrict upstream portions)
- §11: Can't impose additional restrictions preventing exercise of license rights

**Effect:** Downstream recipients can use the Work with most other permissive licenses.

---

## Philosophical Questions

### What's the difference between steelmanning and being nice?

**Steelmanning is about intellectual honesty, not niceness.**

**Being nice:** "I don't want to hurt your feelings, so I won't critique."  
**Steelmanning:** "I'll critique rigorously, but I'll engage with your strongest arguments, not weak misrepresentations."

**You can steelman harshly:**
> "Even in its strongest form—assuming perfect data and optimal conditions—this approach fails because [specific evidence]. Here's why..."

**Harsh but honest > nice but dishonest.**

### Is the steelman principle enforceable?

**No** (§4 states it's aspirational).

Courts can't judge whether someone engaged with the "strongest version" of an idea. That's philosophical, not legal.

**But:**
- Community can note violations
- Reputation effects are real
- Persistent strawmanning may indicate bad faith (relevant in disputes)

### Why "receipts" instead of "changelog" or "documentation"?

**Cultural resonance:** "Receipts" comes from social media culture meaning "proof" or "evidence."

**Connotation:** More than just a changelog—it's *evidence of what you did and how you tested it.*

**Attitude:** "Show me the receipts" = "prove it" (which is exactly what we want).

### What if someone uses my receipts to attack me?

**That would violate the steelman principle** (§4).

If someone uses your honest documentation of testing (or lack thereof) to strawman your work, the community should call that out.

**Example:**

You write: "Testing performed: No. These are experimental modifications."

Bad actor says: "See? They didn't test anything! This is garbage!"

**Community response:** "They were honest about testing status. That's what the license requires. Your criticism should engage with the modifications themselves, not the testing status they transparently disclosed."

### Does this license assume everyone acts in good faith?

**No, it enforces good faith through legal requirements.**

- §2: Receipts and transparency (enforced)
- §3: Prohibited misrepresentations (enforced)
- §4: Steelman principle (aspirational but community-policed)
- §9: Termination for violations (enforced)

**Bad actors can be dealt with:**
- Document non-compliance (§10)
- Terminate license (§9)
- Potential legal action for damages

### Is this license "anti-corporate"?

**No.** It's explicitly permissive for commercial use.

**What it prevents:**
- Misrepresenting results to boost sales
- Claiming unmodified upstream results for your product
- Hiding modifications that change behavior

**What it allows:**
- Commercial products using the Work
- Proprietary modifications (with receipts)
- Selling services based on the Work
- Enterprise deployment

**If anything, it's pro-intellectual-honesty, which corporations should appreciate.**

---

## Practical Scenarios

### Scenario: I'm a grad student. Can I use this in my thesis?

**Yes, absolutely.**

Include in your thesis:
- Attribution to the Work
- Receipts in appendix if you modified it
- Link to original repository
- Distinguish your modifications from upstream

This is already good academic practice.

### Scenario: I want to create a commercial SaaS product.

**Yes, you can.**

**Requirements:**
1. Send participation invitation within 30 days of launch
2. Provide attribution in product documentation/about page
3. If you modified the code, maintain internal receipts
4. If you make performance claims, disclose methodology (§2.4)

**You don't have to:**
- Open-source your product
- Share your modifications publicly
- Pay royalties

### Scenario: I want to teach a course using this.

**Perfect use case.**

For students:
- Use freely
- Modify for assignments
- No receipts needed (internal use)

For course materials:
- Include attribution in syllabus
- Link to original repository
- Note any modifications to examples

### Scenario: I'm writing a paper comparing different methods.

**Great!**

If you're comparing the Work to other methods:
- Disclose configurations used (§2.4)
- Link to documentation
- Provide command lines / parameters
- Enable reproduction

**This is what makes science reproducible.**

### Scenario: I found a bug. Can I fix it and distribute?

**Yes.**

1. Fix the bug
2. Create brief receipts (1-2 lines changed, how you tested)
3. Distribute with attribution and receipts
4. Consider contributing the fix upstream (not required but appreciated)

### Scenario: I'm creating a fork because upstream is inactive.

**That's fine.**

1. Fork the repository
2. Make your improvements
3. Create receipts documenting changes
4. Send participation invitation to original author
5. Clearly mark as a fork in README

**This is exactly what open source is for.**

### Scenario: Can I sell training/consulting on this Work?

**Yes, freely.**

Selling services (training, consulting, support) doesn't trigger any license requirements beyond basic attribution.

You don't need to provide receipts for training materials (unless you're distributing modified code).

### Scenario: I'm integrating this into a larger open-source project.

**Great!**

Include:
- LICENSE file from this Work
- Attribution in your project's credits
- If modified, include receipts
- Note which components are Steelman-licensed

Your larger project can be under a different compatible license (MIT, BSD, Apache).

---

## Edge Cases

### What if I modify the Work but don't realize it's licensed?

**Cure period applies** (§9).

Once you discover the license requirements:
- You have 30 days to come into compliance
- Add receipts, attribution, etc.
- Good faith effort to comply restores your license

### What if receipts requirements change in a new version?

**You can choose any version** (§13).

If you received the Work under v1.0, you can continue using v1.0 requirements even if v2.0 has different requirements.

Or you can adopt v2.0 voluntarily.

### What if the original author is unreachable for participation invite?

**Document your good faith efforts:**

- Where you looked (repo, email, GitHub, website)
- When you tried (dates)
- Methods used (email, issues, etc.)

Courts recognize good faith compliance attempts.

### What if someone claims I violated but I believe I complied?

**Dispute resolution** (§10):

1. **Discussion:** Talk it out
2. **Mediation:** Neutral third party
3. **Documentation:** Public statement of positions
4. **Court:** Last resort

Most disputes resolve at step 1 or 2 with good faith.

### Can AI-generated code be under this license?

**Yes, if you own the copyright.**

If you use AI (like Claude, GPT, etc.) to help develop:
- You likely own the copyright (check your jurisdiction)
- License the output under Steelman
- In receipts, note that AI assistance was used (transparency)

**Note:** Some AI terms of service affect ownership—check those.

### What about code written before this license existed?

**Relicensing is your choice.**

If you hold the copyright, you can:
- Relicense your existing code under Steelman
- Keep old versions under old license
- New versions under Steelman

If multiple contributors, get their agreement for relicensing.

---

## Getting Help

### I have a question not answered here.

**Resources:**
1. Read the full license text (LICENSE.md)
2. Read the NOTICE file (NOTICE.md)
3. Check project documentation
4. Open a Discussion on GitHub
5. Email (see repository for contact)

### I want to use this license for my project.

**Steps:**
1. Copy LICENSE.md to your repository
2. Add copyright notice with your name and year
3. Create NOTICE.md (adapt the template)
4. Add license badge to README
5. Document in CONTRIBUTING.md

**Optional but recommended:**
- Add receipts template
- Add FAQ (adapt this one)
- Explain why you chose this license

### I think someone is violating this license.

**First:**
- Assume good faith (they might not realize)
- Document the violation clearly
- Contact them privately first

**Then:**
- Point them to license requirements
- Offer to help them comply
- Give them 30 days to cure

**If no response:**
- Public documentation of non-compliance
- Consider legal consultation
- License termination

**Philosophy:** Educate before escalating.

### Where can I learn more about the philosophy?

**Fractal Reality project:**
- Layers 0-12: Complete framework
- Layer 9: Ethics and validation
- "Liberating Inarticulate Genius": Steelman principle
- GitHub discussions: Community Q&A

**General resources:**
- Open Source Initiative (OSI.org)
- Software Freedom Law Center (SFLC.org)
- TL;DR Legal (for license comparisons)

---

## License Evolution

### Will this license change?

**Maybe.** Version 2.0 is current (October 2025).

**If it changes:**
- Breaking changes → major version (3.0, 4.0)
- Clarifications → minor version (2.1, 2.2)
- You can stick with version you received (§13)

### How can I propose changes to the license?

Open a Discussion on the Fractal Reality GitHub repository with:
- Proposed change
- Rationale (why needed)
- Impact analysis (who it affects, how)
- Alternative considered

License steward (Ashman Roonz) will consider community feedback.

### Can I create my own variation?

**Technically yes, legally complex.**

You can:
- Create a new license inspired by this one
- Change the name (can't call it "Steelman License")
- Adjust terms for your needs

**Better approach:** Propose changes to this license so community benefits.

---

```
∞ ↔ •
```

**Questions about [ICE] validation, aperture theory, or Fractal Reality framework?**  
See project documentation: https://github.com/AshmanRoonz/Fractal_Reality

**Questions about open source licensing in general?**  
See: https://choosealicense.com, https://opensource.org

---

*"Steelman first, receipts always. Ground in reality, honor sources, enable verification."*

**Version 2.0 — October 2025**
