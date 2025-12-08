from django.core.management.base import BaseCommand
from courses.models import Course, Lesson


class Command(BaseCommand):
    help = 'Cria cursos e aulas iniciais'

    def handle(self, *args, **options):
        courses_data = [
            {
                'title': 'Logica de Programacao para Iniciantes',
                'description': 'Aprenda os fundamentos da logica de programacao com exemplos praticos. Este curso e ideal para quem esta comecando na area de tecnologia e quer entender como pensar de forma logica para resolver problemas.',
                'level': 'beginner',
                'area': 'programming',
                'duration_hours': 20,
                'skills_taught': 'logica, algoritmos, pseudocodigo, fluxogramas, programacao basica',
                'is_free': True,
                'lessons': [
                    {'title': 'Introducao a Logica', 'content': 'O que e logica de programacao e por que e importante aprender antes de qualquer linguagem.', 'order': 1},
                    {'title': 'Variaveis e Tipos de Dados', 'content': 'Entenda o que sao variaveis, tipos de dados primitivos e como armazena-los.', 'order': 2},
                    {'title': 'Operadores', 'content': 'Operadores aritmeticos, relacionais e logicos.', 'order': 3},
                    {'title': 'Estruturas Condicionais', 'content': 'If, else, switch e como tomar decisoes no codigo.', 'order': 4},
                    {'title': 'Estruturas de Repeticao', 'content': 'For, while, do-while e quando usar cada um.', 'order': 5},
                ]
            },
            {
                'title': 'Fundamentos de Banco de Dados',
                'description': 'Domine os conceitos essenciais de bancos de dados relacionais. Aprenda SQL desde o basico ate consultas avancadas.',
                'level': 'beginner',
                'area': 'data_science',
                'duration_hours': 25,
                'skills_taught': 'sql, banco de dados, mysql, postgresql, modelagem de dados',
                'is_free': True,
                'lessons': [
                    {'title': 'O que sao Bancos de Dados', 'content': 'Introducao aos conceitos de bancos de dados e sua importancia.', 'order': 1},
                    {'title': 'Modelagem de Dados', 'content': 'Entidades, atributos, relacionamentos e normalizacao.', 'order': 2},
                    {'title': 'SQL Basico - SELECT', 'content': 'Como consultar dados com SELECT, WHERE, ORDER BY.', 'order': 3},
                    {'title': 'SQL Intermediario - JOINs', 'content': 'INNER JOIN, LEFT JOIN, RIGHT JOIN e FULL JOIN.', 'order': 4},
                    {'title': 'INSERT, UPDATE e DELETE', 'content': 'Manipulando dados no banco.', 'order': 5},
                ]
            },
            {
                'title': 'Introducao ao Django',
                'description': 'Aprenda a criar aplicacoes web completas com Django, o framework Python mais popular. Do zero ao deploy.',
                'level': 'intermediate',
                'area': 'programming',
                'duration_hours': 40,
                'skills_taught': 'python, django, web development, mvc, orm, rest api',
                'is_free': False,
                'price': 99.90,
                'lessons': [
                    {'title': 'Configurando o Ambiente', 'content': 'Instalando Python, Django e criando seu primeiro projeto.', 'order': 1},
                    {'title': 'Models e ORM', 'content': 'Criando modelos e interagindo com o banco de dados.', 'order': 2},
                    {'title': 'Views e URLs', 'content': 'Roteamento e processamento de requisicoes.', 'order': 3},
                    {'title': 'Templates', 'content': 'Criando interfaces HTML dinamicas com Django Templates.', 'order': 4},
                    {'title': 'Formularios', 'content': 'Criando e validando formularios.', 'order': 5},
                    {'title': 'Autenticacao', 'content': 'Sistema de login, logout e registro de usuarios.', 'order': 6},
                ]
            },
            {
                'title': 'Excel e Automacao (VBA Basico)',
                'description': 'Aprenda a automatizar tarefas repetitivas no Excel usando VBA. Ideal para profissionais que querem aumentar sua produtividade.',
                'level': 'beginner',
                'area': 'other',
                'duration_hours': 15,
                'skills_taught': 'excel, vba, automacao, macros, planilhas',
                'is_free': True,
                'lessons': [
                    {'title': 'Introducao ao VBA', 'content': 'O que e VBA e como acessar o editor.', 'order': 1},
                    {'title': 'Gravando Macros', 'content': 'Como gravar e executar macros simples.', 'order': 2},
                    {'title': 'Variaveis e Tipos no VBA', 'content': 'Declarando variaveis e tipos de dados.', 'order': 3},
                    {'title': 'Estruturas de Controle', 'content': 'If, For, While no VBA.', 'order': 4},
                    {'title': 'Manipulando Celulas', 'content': 'Range, Cells e como trabalhar com dados.', 'order': 5},
                ]
            },
            {
                'title': 'Python para Data Science',
                'description': 'Aprenda Python focado em analise de dados com Pandas, NumPy e visualizacao com Matplotlib.',
                'level': 'intermediate',
                'area': 'data_science',
                'duration_hours': 35,
                'skills_taught': 'python, pandas, numpy, matplotlib, data science, analise de dados',
                'is_free': False,
                'price': 149.90,
                'lessons': [
                    {'title': 'Ambiente de Data Science', 'content': 'Jupyter Notebook, Anaconda e bibliotecas essenciais.', 'order': 1},
                    {'title': 'NumPy Essencial', 'content': 'Arrays, operacoes e funcoes matematicas.', 'order': 2},
                    {'title': 'Pandas - DataFrames', 'content': 'Carregando, explorando e manipulando dados.', 'order': 3},
                    {'title': 'Limpeza de Dados', 'content': 'Tratando valores nulos, duplicados e inconsistencias.', 'order': 4},
                    {'title': 'Visualizacao com Matplotlib', 'content': 'Graficos de linha, barra, pizza e scatter.', 'order': 5},
                ]
            },
        ]

        created_count = 0
        for course_data in courses_data:
            lessons_data = course_data.pop('lessons', [])
            
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults=course_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Curso criado: {course.title}')
                
                for lesson_data in lessons_data:
                    Lesson.objects.create(course=course, **lesson_data)
                    self.stdout.write(f'  - Aula criada: {lesson_data["title"]}')
            else:
                self.stdout.write(f'Curso ja existe: {course.title}')

        self.stdout.write(self.style.SUCCESS(f'\n{created_count} cursos criados com sucesso!'))
