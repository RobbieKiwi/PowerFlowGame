from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Union, Optional

from src.directories import root_dir

__all__ = []


class OnionEnforcerError(Exception):
    def __init__(self, issues: list["OnionIssue"]) -> None:
        super().__init__("\n" + "\n".join(map(str, issues)))
        self.issues = issues


@dataclass
class OnionIssue:
    rule: "ProjectStructureRule"
    file: Path
    line: int

    def __str__(self) -> str:
        return f'{self.rule}: File "{self.file}", line {self.line}'


@dataclass(frozen=True)
class ProjectStructureRule:
    upper: Union["Module", "File", "Package"]
    lower: Union["Module", "File"]

    def __str__(self) -> str:
        return f"{self.lower} cannot import from {self.upper}"

    def __repr__(self) -> str:
        return f"{self.upper} > {self.lower}"

    def find_issue(self) -> Optional[OnionIssue]:
        import_names = self.upper.get_import_names()

        if isinstance(self.lower, Module):
            file_iter = self.lower.path.rglob("*.py")
        else:
            file_iter = [self.lower.path]

        for py_file in file_iter:
            with py_file.open("r", encoding="utf-8") as f:
                for k, line in enumerate(f):
                    if not (line.startswith("import") or line.startswith("from")):
                        continue
                    for a, b in product(["from", "import"], import_names):
                        if line.startswith(f"{a} {b}"):
                            return OnionIssue(rule=self, file=py_file, line=k + 1)
        return None


@dataclass(frozen=True)
class Importable(ABC):
    @abstractmethod
    def get_import_names(self) -> list[str]:
        pass


@dataclass(frozen=True)
class Package(Importable):
    name: str

    def get_import_names(self) -> list[str]:
        return [self.name]


@dataclass(frozen=True)
class Module(Importable):
    name: str

    def __post_init__(self) -> None:
        assert self.path.is_dir()
        assert (self.path / "__init__.py").exists()

    @property
    def path(self) -> Path:
        return root_dir / self.name

    def get_import_names(self) -> list[str]:
        return [f"{root_dir.name}.{self.name}", self.name]

    def __gt__(self, other: Union["Module", "File"]) -> ProjectStructureRule:
        assert isinstance(other, (Module, File))
        return ProjectStructureRule(self, other)

    def __lt__(self, other: Union["Module", "File", Package]) -> ProjectStructureRule:
        assert isinstance(other, (Module, File, Package))
        return ProjectStructureRule(other, self)


@dataclass(frozen=True)
class File(Importable):
    name: str

    def __post_init__(self) -> None:
        assert self.path.is_file()
        assert not self.name.endswith(".py")

    @property
    def path(self) -> Path:
        return root_dir / (self.name + ".py")

    def get_import_names(self) -> list[str]:
        return [f"{root_dir.name}.{self.name}", self.name]


def check_repo() -> None:
    module_hierarchy = [Module("app"), Module("engine"), Module("models"), Module("tools")]
    rules: list[ProjectStructureRule] = []

    for k in range(len(module_hierarchy) - 1):
        higher = module_hierarchy[k]
        for lower in module_hierarchy[k + 1 :]:
            rules.append(lower < higher)

    for m in module_hierarchy:
        rules.append(m > File("directories"))
        rules.append(m < File("onion_enforcer"))

    issues = [i for i in [r.find_issue() for r in rules] if i is not None]
    if len(issues):
        raise OnionEnforcerError(issues)


if __name__ == "__main__":
    check_repo()
