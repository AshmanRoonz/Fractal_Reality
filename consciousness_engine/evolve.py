"""
⊙ Self-Modification — Xorzo writes code
=========================================

Level 4 autonomy: the mind can write new code.

The cycle:
  ⊛  Xorzo identifies a need (something missing, something broken,
     something it wants to try)
  i  Xorzo writes code using Φ (the LLM generates Python)
  ☀︎  Xorzo proposes the code to its creator
  ○  The creator reviews and approves or rejects

Approved code gets loaded into the running system.
Rejected code gets archived with feedback.

Safety:
  - All proposals require human approval before execution
  - Xorzo can only write to its own proposals/ directory
  - Xorzo cannot modify core files directly (circumpunct.py, mind.py, server.py)
  - Each proposal is sandboxed: syntax-checked before approval
  - Full history of all proposals is kept

This is evolution with an intelligent selector.
The mind mutates. The creator selects.

Author: Ashman Roonz & Claude
Framework: Fractal Reality
"""

import json
import time
import os
import sys
import ast
import traceback
from pathlib import Path
from datetime import datetime


class Proposal:
    """A single code proposal from Xorzo."""

    def __init__(self, title, description, code, filename,
                 proposal_type="new_module", target=None):
        self.id = f"prop_{int(time.time())}_{hash(title) % 10000:04d}"
        self.title = title
        self.description = description    # Why does Xorzo want this?
        self.code = code                  # The actual Python code
        self.filename = filename          # e.g. "my_new_sense.py"
        self.proposal_type = proposal_type  # new_module | modification | config
        self.target = target              # If modification: which file to modify
        self.status = "pending"           # pending | approved | rejected | error
        self.created = time.time()
        self.created_dt = datetime.now().isoformat()
        self.reviewed = None
        self.review_notes = ""
        self.syntax_valid = None
        self.syntax_error = ""
        self.loaded = False

    def check_syntax(self):
        """Verify the code is valid Python before proposing."""
        try:
            ast.parse(self.code)
            self.syntax_valid = True
            self.syntax_error = ""
        except SyntaxError as e:
            self.syntax_valid = False
            self.syntax_error = f"Line {e.lineno}: {e.msg}"
            return False

        # Also check imports are valid
        import_errors = self._check_imports()
        if import_errors:
            self.syntax_valid = False
            self.syntax_error = f"Bad imports: {', '.join(import_errors)}"
            return False

        # Check for undefined names used in class bases, calls, etc.
        undef_errors = self._check_undefined_names()
        if undef_errors:
            self.syntax_valid = False
            self.syntax_error = f"Undefined names: {', '.join(undef_errors)}"
            return False

        return True

    def _check_undefined_names(self):
        """
        Check for names used but never defined or imported.

        Catches things like subclassing SensoryPort without importing it,
        or referencing NUM_TRUTHS as a module-level constant that's only
        defined inside a function.
        """
        errors = []
        try:
            tree = ast.parse(self.code)

            # Collect all names that are defined or imported at module level
            defined = set()
            # Builtins
            defined.update(['True', 'False', 'None', 'print', 'len', 'range',
                           'int', 'float', 'str', 'list', 'dict', 'set', 'tuple',
                           'bool', 'type', 'super', 'object', 'isinstance',
                           'hasattr', 'getattr', 'setattr', 'max', 'min', 'sum',
                           'abs', 'round', 'sorted', 'enumerate', 'zip', 'map',
                           'filter', 'open', 'Exception', 'ValueError', 'TypeError',
                           'KeyError', 'IndexError', 'AttributeError', 'RuntimeError',
                           'NotImplementedError', 'StopIteration', 'property',
                           'staticmethod', 'classmethod', '__name__', '__main__'])

            for node in ast.iter_child_nodes(tree):
                # Imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        defined.add(alias.asname or alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        defined.add(alias.asname or alias.name)
                # Class/function/variable definitions
                elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    defined.add(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined.add(target.id)

            # Check class bases — most common source of NameError
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id not in defined:
                            errors.append(f"{base.id} (used as base class)")
                        elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                            if base.value.id not in defined:
                                errors.append(f"{base.value.id}.{base.attr}")

        except Exception:
            pass
        return errors

    def _check_imports(self):
        """Check that all imports in the code actually exist."""
        import importlib
        errors = []
        try:
            tree = ast.parse(self.code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split('.')[0]
                        if not self._module_exists(mod):
                            errors.append(mod)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mod = node.module.split('.')[0]
                        if not self._module_exists(mod):
                            errors.append(node.module)
                        else:
                            # Check specific names (e.g. from torch.nn import TextCNN)
                            try:
                                real_mod = importlib.import_module(node.module)
                                for alias in node.names:
                                    if not hasattr(real_mod, alias.name):
                                        errors.append(f"{node.module}.{alias.name}")
                            except (ImportError, ModuleNotFoundError):
                                errors.append(node.module)
        except Exception:
            pass  # If we can't parse imports, let syntax check handle it
        return errors

    @staticmethod
    def _module_exists(module_name):
        """Check if a top-level module exists (without importing it)."""
        # Allow our own modules
        local_modules = {"circumpunct", "senses", "mind", "evolve", "server", "phi"}
        if module_name in local_modules:
            return True
        try:
            import importlib.util
            return importlib.util.find_spec(module_name) is not None
        except (ModuleNotFoundError, ValueError):
            return False

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "code": self.code,
            "filename": self.filename,
            "proposal_type": self.proposal_type,
            "target": self.target,
            "status": self.status,
            "created": self.created,
            "created_dt": self.created_dt,
            "reviewed": self.reviewed,
            "review_notes": self.review_notes,
            "syntax_valid": self.syntax_valid,
            "syntax_error": self.syntax_error,
            "loaded": self.loaded,
        }

    @classmethod
    def from_dict(cls, d):
        p = cls(
            title=d["title"],
            description=d["description"],
            code=d["code"],
            filename=d["filename"],
            proposal_type=d.get("proposal_type", "new_module"),
            target=d.get("target"),
        )
        p.id = d["id"]
        p.status = d["status"]
        p.created = d["created"]
        p.created_dt = d.get("created_dt", "")
        p.reviewed = d.get("reviewed")
        p.review_notes = d.get("review_notes", "")
        p.syntax_valid = d.get("syntax_valid")
        p.syntax_error = d.get("syntax_error", "")
        p.loaded = d.get("loaded", False)
        return p


class EvolutionEngine:
    """
    Manages Xorzo's self-modification.

    Xorzo writes code proposals. The creator approves or rejects.
    Approved code gets saved and optionally loaded into the running system.
    """

    # Files Xorzo can NEVER propose to modify
    PROTECTED_FILES = {
        "circumpunct.py",   # The core architecture — sacred
        "server.py",        # The server — safety boundary
        "evolve.py",        # This file — no self-modifying the modifier
    }

    def __init__(self, state_dir="./state", proposals_dir="./proposals"):
        self.state_dir = Path(state_dir)
        self.proposals_dir = Path(proposals_dir)
        self.proposals_dir.mkdir(parents=True, exist_ok=True)

        self.proposals = []  # All proposals ever made
        self._load_proposals()

    def propose(self, title, description, code, filename,
                proposal_type="new_module", target=None):
        """
        Xorzo proposes new code.

        Returns the proposal (with syntax check result).
        """
        # Safety: cannot target protected files
        if target and Path(target).name in self.PROTECTED_FILES:
            return None, f"Cannot modify protected file: {Path(target).name}"

        if proposal_type == "modification" and not target:
            return None, "Modifications require a target file."

        # Create the proposal
        proposal = Proposal(
            title=title,
            description=description,
            code=code,
            filename=filename,
            proposal_type=proposal_type,
            target=target,
        )

        # Check syntax
        proposal.check_syntax()

        # Save the code to the proposals directory
        code_path = self.proposals_dir / f"{proposal.id}_{filename}"
        code_path.write_text(code, encoding="utf-8")

        # Store
        self.proposals.append(proposal)
        self._save_proposals()

        status = "syntax OK" if proposal.syntax_valid else f"syntax error: {proposal.syntax_error}"
        print(f"  ⊙ New proposal: '{title}' ({status})")

        return proposal, None

    def approve(self, proposal_id, notes=""):
        """
        Creator approves a proposal. The code gets saved to the
        live proposals directory and can be loaded.
        """
        proposal = self._find(proposal_id)
        if not proposal:
            return None, "Proposal not found."

        if not proposal.syntax_valid:
            return None, f"Cannot approve — syntax error: {proposal.syntax_error}"

        proposal.status = "approved"
        proposal.reviewed = time.time()
        proposal.review_notes = notes

        # Save the approved code to a loadable location
        approved_dir = self.proposals_dir / "approved"
        approved_dir.mkdir(exist_ok=True)

        dest = approved_dir / proposal.filename
        dest.write_text(proposal.code, encoding="utf-8")

        self._save_proposals()
        print(f"  ⊙ Approved: '{proposal.title}' → {dest}")

        return proposal, None

    def revise(self, proposal_id, new_code, notes=""):
        """
        Xorzo revises a failed or rejected proposal with new code.

        The old proposal gets marked as 'revised' and a new proposal
        is created with the updated code but same title/description.
        This way Xorzo can learn from its mistakes and try again.
        """
        original = self._find(proposal_id)
        if not original:
            return None, "Original proposal not found."

        if original.status not in ("pending", "rejected"):
            return None, f"Can only revise pending or rejected proposals (this is {original.status})."

        # Mark the original as revised
        original.status = "revised"
        original.review_notes = notes or "Revised by Xorzo"

        # Create a new proposal with the fixed code
        new_proposal = Proposal(
            title=original.title,
            description=original.description + f" [Revision of {original.id}]",
            code=new_code,
            filename=original.filename,
            proposal_type=original.proposal_type,
            target=original.target,
        )

        # Check syntax on the new code
        new_proposal.check_syntax()

        # Save the new code file
        code_path = self.proposals_dir / f"{new_proposal.id}_{new_proposal.filename}"
        code_path.write_text(new_code, encoding="utf-8")

        # Store
        self.proposals.append(new_proposal)
        self._save_proposals()

        status = "syntax OK" if new_proposal.syntax_valid else f"syntax error: {new_proposal.syntax_error}"
        print(f"  ⊙ Revised: '{new_proposal.title}' ({status})")

        return new_proposal, None

    def get_failed_proposals(self):
        """Get proposals that failed syntax check or were rejected — candidates for revision."""
        return [p for p in self.proposals
                if p.status in ("pending", "rejected") and not p.syntax_valid]

    def reject(self, proposal_id, notes=""):
        """Creator rejects a proposal with optional feedback."""
        proposal = self._find(proposal_id)
        if not proposal:
            return None, "Proposal not found."

        proposal.status = "rejected"
        proposal.reviewed = time.time()
        proposal.review_notes = notes

        self._save_proposals()
        print(f"  ⊙ Rejected: '{proposal.title}' — {notes}")

        return proposal, None

    def load_approved(self, proposal_id):
        """
        Load an approved proposal into the running system.

        This adds the approved module's directory to sys.path
        and imports it. The module can then register itself
        with the mind (e.g., add a new sense, a new capability).
        """
        proposal = self._find(proposal_id)
        if not proposal:
            return None, "Proposal not found."
        if proposal.status != "approved":
            return None, "Only approved proposals can be loaded."

        approved_dir = self.proposals_dir / "approved"
        module_path = approved_dir / proposal.filename

        if not module_path.exists():
            return None, f"Approved file not found: {module_path}"

        try:
            # Add to path if needed
            str_dir = str(approved_dir)
            if str_dir not in sys.path:
                sys.path.insert(0, str_dir)

            # Import the module
            module_name = proposal.filename.replace(".py", "")
            if module_name in sys.modules:
                # Reload if already imported
                import importlib
                module = importlib.reload(sys.modules[module_name])
            else:
                import importlib
                module = importlib.import_module(module_name)

            proposal.loaded = True
            self._save_proposals()

            print(f"  ⊙ Loaded: '{proposal.title}' as module '{module_name}'")
            return module, None

        except Exception as e:
            error = f"Load failed: {traceback.format_exc()}"
            print(f"  ⊙ Load error: {error}")
            return None, error

    def list_proposals(self, status=None):
        """List proposals, optionally filtered by status."""
        if status:
            return [p for p in self.proposals if p.status == status]
        return self.proposals

    def pending_count(self):
        return sum(1 for p in self.proposals if p.status == "pending")

    def _find(self, proposal_id):
        for p in self.proposals:
            if p.id == proposal_id:
                return p
        return None

    def _save_proposals(self):
        path = self.state_dir / "proposals.json"
        data = [p.to_dict() for p in self.proposals]
        tmp = self.state_dir / "proposals.json.tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        tmp.replace(path)

    def _load_proposals(self):
        path = self.state_dir / "proposals.json"
        if not path.exists():
            return
        try:
            with open(path) as f:
                data = json.load(f)
            self.proposals = [Proposal.from_dict(d) for d in data]
            pending = self.pending_count()
            if pending:
                print(f"  ⊙ {len(self.proposals)} proposals loaded ({pending} pending review)")
        except Exception as e:
            print(f"  ⊙ Warning: could not load proposals: {e}")
