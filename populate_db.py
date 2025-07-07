#!/usr/bin/env python3
"""
Script para popular o banco de dados do MinasLê com dados de exemplo
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.models.minasle_models import db, Escola, Usuario, Livro, AtividadeGamificacao
from src.main import app

def populate_database():
    """Popula o banco de dados com dados de exemplo"""
    
    with app.app_context():
        print("Criando dados de exemplo para o MinasLê...")
        
        # Criar escolas
        escolas = [
            Escola(nome="Escola Estadual Tiradentes", cidade="Pouso Alegre", estado="Minas Gerais"),
            Escola(nome="Colégio Municipal Santos Dumont", cidade="Varginha", estado="Minas Gerais"),
            Escola(nome="Instituto Educacional Machado de Assis", cidade="Poços de Caldas", estado="Minas Gerais"),
            Escola(nome="Escola Técnica José de Alencar", cidade="Três Corações", estado="Minas Gerais")
        ]
        
        for escola in escolas:
            db.session.add(escola)
        
        db.session.commit()
        print(f"✓ Criadas {len(escolas)} escolas")
        
        # Criar usuários pedagogos
        pedagogos = [
            Usuario(nome="Maria Silva", email="maria.silva@escola.mg.gov.br", tipo_usuario="pedagogo", escola_id=1),
            Usuario(nome="João Santos", email="joao.santos@escola.mg.gov.br", tipo_usuario="pedagogo", escola_id=2),
            Usuario(nome="Ana Costa", email="ana.costa@escola.mg.gov.br", tipo_usuario="pedagogo", escola_id=3)
        ]
        
        for pedagogo in pedagogos:
            pedagogo.set_senha("123456")  # Senha padrão para demonstração
            db.session.add(pedagogo)
        
        # Criar usuários alunos
        alunos = [
            Usuario(nome="Carlos Oliveira", email="carlos.oliveira@aluno.mg.gov.br", tipo_usuario="aluno", escola_id=1),
            Usuario(nome="Fernanda Lima", email="fernanda.lima@aluno.mg.gov.br", tipo_usuario="aluno", escola_id=1),
            Usuario(nome="Pedro Souza", email="pedro.souza@aluno.mg.gov.br", tipo_usuario="aluno", escola_id=2),
            Usuario(nome="Julia Mendes", email="julia.mendes@aluno.mg.gov.br", tipo_usuario="aluno", escola_id=2),
            Usuario(nome="Rafael Pereira", email="rafael.pereira@aluno.mg.gov.br", tipo_usuario="aluno", escola_id=3),
            Usuario(nome="Beatriz Alves", email="beatriz.alves@aluno.mg.gov.br", tipo_usuario="aluno", escola_id=3)
        ]
        
        for aluno in alunos:
            aluno.set_senha("123456")  # Senha padrão para demonstração
            db.session.add(aluno)
        
        db.session.commit()
        print(f"✓ Criados {len(pedagogos)} pedagogos e {len(alunos)} alunos")
        
        # Criar livros (incluindo obras regionais de Minas Gerais)
        livros = [
            # Obras regionais de Minas Gerais
            Livro(
                titulo="Grande Sertão: Veredas",
                autor="João Guimarães Rosa",
                genero="Romance",
                obra_regional=True,
                descricao="Obra-prima da literatura brasileira ambientada no sertão mineiro.",
                capa_url="https://example.com/grande_sertao_veredas.jpg"
            ),
            Livro(
                titulo="O Cortiço do Inferno",
                autor="Carlos Drummond de Andrade",
                genero="Poesia",
                obra_regional=True,
                descricao="Coletânea de poemas do grande poeta itabirano.",
                capa_url="https://example.com/drummond_poesias.jpg"
            ),
            Livro(
                titulo="Lendas e Tradições de Minas",
                autor="Bernardo Guimarães",
                genero="Folclore",
                obra_regional=True,
                descricao="Compilação de lendas e tradições do folclore mineiro.",
                capa_url="https://example.com/lendas_minas.jpg"
            ),
            Livro(
                titulo="A Escrava Isaura",
                autor="Bernardo Guimarães",
                genero="Romance",
                obra_regional=True,
                descricao="Romance clássico da literatura brasileira ambientado em Minas Gerais.",
                capa_url="https://example.com/escrava_isaura.jpg"
            ),
            # Obras nacionais e internacionais
            Livro(
                titulo="Dom Casmurro",
                autor="Machado de Assis",
                genero="Romance",
                obra_regional=False,
                descricao="Clássico da literatura brasileira sobre ciúme e dúvida.",
                capa_url="https://example.com/dom_casmurro.jpg"
            ),
            Livro(
                titulo="O Pequeno Príncipe",
                autor="Antoine de Saint-Exupéry",
                genero="Fábula",
                obra_regional=False,
                descricao="História atemporal sobre amizade, amor e perda.",
                capa_url="https://example.com/pequeno_principe.jpg"
            ),
            Livro(
                titulo="1984",
                autor="George Orwell",
                genero="Ficção Científica",
                obra_regional=False,
                descricao="Distopia sobre vigilância e controle totalitário.",
                capa_url="https://example.com/1984.jpg"
            ),
            Livro(
                titulo="O Cortiço",
                autor="Aluísio Azevedo",
                genero="Romance",
                obra_regional=False,
                descricao="Romance naturalista sobre a vida em um cortiço no Rio de Janeiro.",
                capa_url="https://example.com/o_cortico.jpg"
            )
        ]
        
        for livro in livros:
            db.session.add(livro)
        
        db.session.commit()
        print(f"✓ Criados {len(livros)} livros ({sum(1 for l in livros if l.obra_regional)} obras regionais)")
        
        # Criar atividades de gamificação
        atividades = [
            AtividadeGamificacao(
                nome="Primeira Leitura",
                descricao="Complete sua primeira leitura no MinasLê",
                pontos=50,
                tipo="leitura_completa"
            ),
            AtividadeGamificacao(
                nome="Leitor Assíduo",
                descricao="Complete 5 leituras",
                pontos=200,
                tipo="leitura_multipla"
            ),
            AtividadeGamificacao(
                nome="Explorador Regional",
                descricao="Leia 3 obras regionais de Minas Gerais",
                pontos=150,
                tipo="obra_regional"
            ),
            AtividadeGamificacao(
                nome="Participação Ativa",
                descricao="Participe de um clube de leitura",
                pontos=75,
                tipo="participacao_clube"
            ),
            AtividadeGamificacao(
                nome="Leitor Dedicado",
                descricao="Mantenha uma sequência de 7 dias lendo",
                pontos=100,
                tipo="sequencia_leitura"
            ),
            AtividadeGamificacao(
                nome="Mestre dos Livros",
                descricao="Complete 10 leituras",
                pontos=500,
                tipo="leitura_multipla"
            )
        ]
        
        for atividade in atividades:
            db.session.add(atividade)
        
        db.session.commit()
        print(f"✓ Criadas {len(atividades)} atividades de gamificação")
        
        print("\n🎉 Banco de dados populado com sucesso!")
        print("\n📊 Resumo dos dados criados:")
        print(f"   • {len(escolas)} escolas")
        print(f"   • {len(pedagogos)} pedagogos")
        print(f"   • {len(alunos)} alunos")
        print(f"   • {len(livros)} livros")
        print(f"   • {len(atividades)} atividades de gamificação")
        
        print("\n🔑 Credenciais de acesso (senha padrão: 123456):")
        print("   Pedagogos:")
        for pedagogo in pedagogos:
            print(f"     • {pedagogo.email}")
        print("   Alunos:")
        for aluno in alunos:
            print(f"     • {aluno.email}")

if __name__ == "__main__":
    populate_database()

