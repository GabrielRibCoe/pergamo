"""CONTRATO do banco de dados (kit do dia 0).

Todos os bancos (memória, SQLite, MongoDB) implementam esta classe. O resto do app só
conhece Repo, nunca sabe qual banco está por trás. Mudou uma assinatura? Avise o grupo.

Formatos devolvidos (dicionários):
    usuário  -> {"id", "nome", "email", "senha_hash", "papel", "criado_em"}
    perfil   -> dicionário descrito em docs/ROTEIRO.md (seção 4.1)
    professor da lista -> {"id", "nome", "email", "perfil": {...}}
    vínculo  -> {"id", "aluno_id", "professor_id", "criado_em"}
    turma    -> [{"id", "nome", "perfil_label"}]   (alunos vinculados a um professor)
"""
from abc import ABC, abstractmethod


class Repo(ABC):
    # ------------------------------------------------------------------ contas
    @abstractmethod
    def create_user(self, email: str, password_hash: str, role: str, name: str) -> str:
        """Cria a conta e devolve o user_id. E-mail repetido: levanta ValueError("email_ja_cadastrado")."""

    @abstractmethod
    def get_user_by_email(self, email: str) -> dict | None:
        """Busca por e-mail (sem diferenciar maiúsculas). None se não existir."""

    @abstractmethod
    def get_user(self, user_id: str) -> dict | None:
        """Busca por id. None se não existir."""

    # ------------------------------------------------------------------ perfil
    @abstractmethod
    def save_profile(self, user_id: str, profile: dict) -> None:
        """Salva (ou substitui) o perfil do usuário."""

    @abstractmethod
    def get_profile(self, user_id: str) -> dict | None:
        """Devolve o perfil ou None se o usuário ainda não preencheu."""

    @abstractmethod
    def list_professors(self) -> list[dict]:
        """Professores que já têm perfil: [{"id", "nome", "email", "perfil"}]."""

    # ------------------------------------------------------------------ vínculos (turmas)
    @abstractmethod
    def create_link(self, student_id: str, teacher_id: str) -> None:
        """Vincula aluno e professor. Aluno já vinculado: levanta ValueError("aluno_ja_vinculado")."""

    @abstractmethod
    def end_link(self, student_id: str) -> None:
        """Desvincula (status encerrado, sem apagar histórico). Sem vínculo ativo: não faz nada."""

    @abstractmethod
    def get_active_link(self, student_id: str) -> dict | None:
        """Vínculo ativo do aluno ou None."""

    @abstractmethod
    def get_roster(self, teacher_id: str) -> list[dict]:
        """Alunos com vínculo ativo com o professor: [{"id", "nome", "perfil_label"}]."""
