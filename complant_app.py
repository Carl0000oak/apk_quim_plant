import flet as ft
from complant.main import analisar_planta, buscar_plantas_por_composto, listar_categorias, carregar_banco
from complant.search.wikipedia import buscar_foto_wikipedia
import threading
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import base64

class CompantApp:
    def __init__(self):
        self.page = None
        self.status_text = None
        self.resultados_area = None
        self.input_planta = None
        self.input_composto = None
        self.df_resultados = None
        self.current_results = None
    
    def show_loading(self, message):
        self.status_text.content.controls[0] = ft.Text("⏳", size=20)
        self.status_text.content.controls[1] = ft.Text(message, size=14, color=ft.Colors.BLUE_700)
        self.status_text.bgcolor = ft.Colors.BLUE_50
        self.page.update()
    
    def show_success(self, message):
        self.status_text.content.controls[0] = ft.Text("✅", size=20)
        self.status_text.content.controls[1] = ft.Text(message, size=14, color=ft.Colors.GREEN_700)
        self.status_text.bgcolor = ft.Colors.GREEN_50
        self.page.update()
    
    def show_error(self, message):
        self.status_text.content.controls[0] = ft.Text("❌", size=20)
        self.status_text.content.controls[1] = ft.Text(message, size=14, color=ft.Colors.RED_700)
        self.status_text.bgcolor = ft.Colors.RED_50
        self.page.update()
    
    def clear_results(self):
        self.resultados_area.controls.clear()
        self.df_resultados = None
        self.current_results = None
        self.page.update()
    
    def criar_tabela_compostos(self, resultados):
        dados = []
        for item in resultados:
            freq = item.get('freq', 0)
            max_freq = max([r.get('freq', 0) for r in resultados]) if resultados else 1
            presence = (freq / max_freq * 100) if max_freq > 0 else 0
            conf = min(freq * 25, 95) if freq > 0 else 0
            rel = min(freq * 35, 95) if freq > 0 else 0
            
            dados.append({
                'Compound': item.get('compound', ''),
                'Freq': freq,
                'Presence': f"{presence:.0f}%",
                'Family': item.get('family', 'Other'),
                'Category': item.get('category', 'Other'),
                'Class': 'Terpenoid' if 'TERPEN' in item.get('family', '').upper() else 'Other',
                'Conf%': conf,
                'Rel': rel,
                'Articles': item.get('articles', 0)
            })
        
        self.df_resultados = pd.DataFrame(dados)
        
        try:
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=list(self.df_resultados.columns),
                    fill_color='#2e7d32',
                    font=dict(color='white', size=11),
                    align='center',
                    height=30
                ),
                cells=dict(
                    values=[self.df_resultados[col] for col in self.df_resultados.columns],
                    fill_color=[['#e8f5e9', '#ffffff'] * len(self.df_resultados)],
                    align='center',
                    font=dict(size=10),
                    height=25
                )
            )])
            
            fig.update_layout(
                height=min(50 + len(dados) * 25, 500),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            
            img_bytes = fig.to_image(format="png", width=800, height=min(50 + len(dados) * 25, 500), scale=1)
            return base64.b64encode(img_bytes).decode()
        except:
            return None
    
    def criar_tabela_funcoes(self, resultados):
        dados = []
        for item in resultados:
            composto = item.get('compound', '')
            funcoes = {
                'agriculture': item.get('agriculture', ['-']),
                'health': item.get('health', ['-']),
                'food': item.get('food', ['-'])
            }
            
            agri = ', '.join(funcoes.get('agriculture', ['-'])[:2]) if funcoes.get('agriculture') and funcoes['agriculture'][0] != '-' else '-'
            health = ', '.join(funcoes.get('health', ['-'])[:2]) if funcoes.get('health') and funcoes['health'][0] != '-' else '-'
            food = ', '.join(funcoes.get('food', ['-'])[:2]) if funcoes.get('food') and funcoes['food'][0] != '-' else '-'
            
            dados.append({
                'Compound': composto,
                'Agriculture': agri,
                'Health': health,
                'Food': food
            })
        
        df = pd.DataFrame(dados)
        
        try:
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=list(df.columns),
                    fill_color='#2e7d32',
                    font=dict(color='white', size=11),
                    align='center',
                    height=30
                ),
                cells=dict(
                    values=[df[col] for col in df.columns],
                    fill_color=[['#e8f5e9', '#ffffff'] * len(df)],
                    align='center',
                    font=dict(size=10),
                    height=25
                )
            )])
            
            fig.update_layout(
                height=min(50 + len(dados) * 25, 500),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            
            img_bytes = fig.to_image(format="png", width=800, height=min(50 + len(dados) * 25, 500), scale=1)
            return base64.b64encode(img_bytes).decode()
        except:
            return None
    
    def criar_propriedades_moleculares(self, resultados):
        smiles_dict = {
            'Citral': 'CC(C)=CCCC(C)=CC=O',
            'Linalool': 'CC(C)=CCCC(C)(C=C)O',
            'Limonene': 'CC1=CCC(CC1)C(C)=C',
            'Myrcene': 'CC(C)=CCCC(C)=C',
            'Geraniol': 'CC(C)=CCCC(C)=CCO',
            'Quercetin': 'OC1=CC(=C(C2=C1C(=O)C(=C(O2)C3=CC(=C(C=C3)O)O)O)O)O',
            'Catechin': 'OC1=CC(=C2C(=C1)OC(C(C2)O)C3=CC(=C(C=C3)O)O)O',
            'Apigenin': 'OC1=CC(=C2C(=C1)OC(=CC2=O)C3=CC=C(C=C3)O)O',
            'Luteolin': 'OC1=CC(=C2C(=C1)OC(=CC2=O)C3=CC(=C(C=C3)O)O)O',
        }
        
        dados = []
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, Lipinski
            
            for item in resultados[:20]:
                comp = item.get('compound', '')
                if comp in smiles_dict:
                    try:
                        mol = Chem.MolFromSmiles(smiles_dict[comp])
                        if mol:
                            dados.append({
                                'Compound': comp,
                                'MW': round(Descriptors.MolWt(mol), 2),
                                'LogP': round(Descriptors.MolLogP(mol), 2),
                                'Donors': Lipinski.NumHDonors(mol),
                                'Acceptors': Lipinski.NumHAcceptors(mol),
                                'RotBonds': Lipinski.NumRotatableBonds(mol),
                                'TPSA': round(Descriptors.TPSA(mol), 2)
                            })
                    except:
                        pass
        except:
            pass
        
        if not dados:
            return None
        
        df = pd.DataFrame(dados)
        
        try:
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=list(df.columns),
                    fill_color='#2e7d32',
                    font=dict(color='white', size=11),
                    align='center',
                    height=30
                ),
                cells=dict(
                    values=[df[col] for col in df.columns],
                    fill_color=[['#e8f5e9', '#ffffff'] * len(df)],
                    align='center',
                    font=dict(size=10),
                    height=25
                )
            )])
            
            fig.update_layout(
                height=min(50 + len(dados) * 25, 500),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            
            img_bytes = fig.to_image(format="png", width=800, height=min(50 + len(dados) * 25, 500), scale=1)
            return base64.b64encode(img_bytes).decode()
        except:
            return None
    
    def criar_grafico_donut(self, resultados):
        if not resultados:
            return None
        
        df = pd.DataFrame(resultados)
        top15 = df.nlargest(15, 'freq') if 'freq' in df.columns else df.head(15)
        
        fig = go.Figure(data=[go.Pie(
            labels=top15['compound'],
            values=top15['freq'] if 'freq' in df.columns else [1]*len(top15),
            hole=0.4,
            textinfo='label+percent',
            textposition='auto',
            marker=dict(colors=px.colors.qualitative.Set3),
            hovertemplate='<b>%{label}</b><br>Frequency: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='Top 15 Compounds',
            height=350,
            width=500,
            template='plotly_white',
            annotations=[dict(text=f'Total: {len(df)} compounds', x=0.5, y=0.5, font_size=14, showarrow=False)]
        )
        
        return fig
    
    def criar_grafico_family_bar(self, resultados):
        if not resultados:
            return None
        
        df = pd.DataFrame(resultados)
        if 'family' not in df.columns:
            return None
        
        df_family = df.groupby('family').agg({
            'freq': 'sum' if 'freq' in df.columns else 'count'
        }).reset_index().sort_values('freq', ascending=True)
        
        fig = go.Figure(data=[go.Bar(
            y=df_family['family'],
            x=df_family['freq'],
            orientation='h',
            text=df_family['freq'],
            textposition='outside',
            marker=dict(
                color=df_family['freq'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Frequency')
            ),
            hovertemplate='<b>%{y}</b><br>Compounds: %{x}<extra></extra>'
        )])
        
        fig.update_layout(
            title='Compounds by Chemical Family',
            xaxis=dict(title='Number of Compounds', gridcolor='#e0e0e0'),
            yaxis=dict(title='Family', gridcolor='#e0e0e0'),
            height=350,
            width=600,
            template='plotly_white',
            margin=dict(l=120)
        )
        
        return fig
    
    def criar_grafico_treemap(self, resultados):
        if not resultados:
            return None
        
        df = pd.DataFrame(resultados)
        if 'category' not in df.columns:
            return None
        
        df_cat = df.groupby('category').agg({
            'freq': 'sum' if 'freq' in df.columns else 'count'
        }).reset_index()
        
        fig = go.Figure(go.Treemap(
            labels=df_cat['category'],
            parents=[''] * len(df_cat),
            values=df_cat['freq'] if 'freq' in df_cat.columns else [1]*len(df_cat),
            textinfo="label+value+percent root",
            marker=dict(colors=px.colors.qualitative.Pastel),
            hovertemplate='<b>%{label}</b><br>Compounds: %{value}<br>Percentage: %{percentRoot:.1%}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Chemical Categories Distribution',
            height=350,
            width=500,
            template='plotly_white'
        )
        
        return fig
    
    def fig_to_base64(self, fig):
        if fig is None:
            return None
        try:
            img_bytes = fig.to_image(format="png", width=600, height=400, scale=1)
            return base64.b64encode(img_bytes).decode()
        except:
            return None
    
    def add_no_image(self):
        self.resultados_area.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("🖼️", size=50),
                    ft.Text("Imagem nao disponivel", size=14, color=ft.Colors.GREY_500),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                bgcolor=ft.Colors.GREY_100,
                border_radius=10,
                width=400,
                height=200,
            )
        )
    
    def display_plant_results(self, planta, resultados, imagem_url):
        self.clear_results()
        
        # TITULO
        self.resultados_area.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("🌿", size=30),
                        ft.Text(planta.title(), size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                    ]),
                    ft.Text(f"{len(resultados)} compostos encontrados", size=14, color=ft.Colors.GREY_700),
                ]),
                padding=15,
                bgcolor=ft.Colors.GREEN_50,
                border_radius=10,
            )
        )
        
        # IMAGEM DA WIKIPEDIA
        if imagem_url:
            try:
                self.resultados_area.controls.append(
                    ft.Container(
                        content=ft.Image(src=imagem_url, width=400, height=250),
                        padding=10,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                    )
                )
            except Exception as e:
                print(f"Erro ao carregar imagem: {e}")
                self.add_no_image()
        else:
            self.add_no_image()
        
        # TABELA DE COMPOSTOS (como imagem)
        img_tabela = self.criar_tabela_compostos(resultados)
        if img_tabela:
            self.resultados_area.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 TABELA DE COMPOSTOS", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                        ft.Image(src=f"data:image/png;base64,{img_tabela}", width=800, height=400),
                    ]),
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=8,
                )
            )
        
        # FUNCOES DOS COMPOSTOS (como imagem)
        img_funcoes = self.criar_tabela_funcoes(resultados)
        if img_funcoes:
            self.resultados_area.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 FUNCOES DOS COMPOSTOS", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                        ft.Image(src=f"data:image/png;base64,{img_funcoes}", width=800, height=300),
                    ]),
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=8,
                )
            )
        
        # PROPRIEDADES MOLECULARES (como imagem)
        img_props = self.criar_propriedades_moleculares(resultados)
        if img_props:
            self.resultados_area.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("🧪 PROPRIEDADES MOLECULARES", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                        ft.Image(src=f"data:image/png;base64,{img_props}", width=800, height=300),
                    ]),
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=8,
                )
            )
        
        # GRAFICO DONUT
        fig_donut = self.criar_grafico_donut(resultados)
        if fig_donut:
            img_b64 = self.fig_to_base64(fig_donut)
            if img_b64:
                self.resultados_area.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📊 GRÁFICO DONUT", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                            ft.Image(src=f"data:image/png;base64,{img_b64}", width=500, height=350),
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=8,
                    )
                )
        
        # GRAFICO FAMILY BAR
        fig_family = self.criar_grafico_family_bar(resultados)
        if fig_family:
            img_b64 = self.fig_to_base64(fig_family)
            if img_b64:
                self.resultados_area.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📊 GRÁFICO FAMILY BAR", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                            ft.Image(src=f"data:image/png;base64,{img_b64}", width=600, height=350),
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=8,
                    )
                )
        
        # GRAFICO TREEMAP
        fig_treemap = self.criar_grafico_treemap(resultados)
        if fig_treemap:
            img_b64 = self.fig_to_base64(fig_treemap)
            if img_b64:
                self.resultados_area.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📊 GRÁFICO TREEMAP", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                            ft.Image(src=f"data:image/png;base64,{img_b64}", width=500, height=350),
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=8,
                    )
                )
        
        self.page.update()
    
    def display_compound_results(self, composto, plantas):
        self.clear_results()
        
        self.resultados_area.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("🧪", size=30),
                        ft.Text(composto.title(), size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                    ]),
                    ft.Text(f"{len(plantas)} plantas encontradas", size=14, color=ft.Colors.GREY_700),
                ]),
                padding=15,
                bgcolor=ft.Colors.GREEN_50,
                border_radius=10,
            )
        )
        
        for planta, artigos in sorted(plantas.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            self.resultados_area.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text("🌿", size=30),
                        ft.Column([
                            ft.Text(planta.title(), size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                            ft.Text(f"📄 {len(artigos)} artigos", size=12, color=ft.Colors.GREY_600),
                        ], spacing=2),
                    ]),
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=8,
                )
            )
        
        self.page.update()
    
    def display_categories(self):
        self.clear_results()
        categorias = listar_categorias()
        
        self.resultados_area.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("📂", size=30),
                        ft.Text("Categorias Disponiveis", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                    ]),
                    ft.Text(f"{len(categorias)} categorias no total", size=14, color=ft.Colors.GREY_700),
                ]),
                padding=15,
                bgcolor=ft.Colors.GREEN_50,
                border_radius=10,
            )
        )
        
        for cat in categorias:
            self.resultados_area.controls.append(
                ft.Container(
                    content=ft.Text(f"• {cat}", size=14, color=ft.Colors.BLACK),
                    padding=5,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=5,
                )
            )
        
        self.page.update()
    
    def display_stats(self):
        self.clear_results()
        
        try:
            from complant.main import db
            stats = db.stats()
            
            self.resultados_area.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📊", size=30),
                            ft.Text("Estatisticas da Base", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_900),
                        ]),
                    ]),
                    padding=15,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10,
                )
            )
            
            cards = ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(stats.get('total', 0)), size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ft.Text("Total de Compostos", size=14, color=ft.Colors.GREY_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(stats.get('categorias', 0)), size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ft.Text("Categorias", size=14, color=ft.Colors.GREY_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(stats.get('versao', '1.0'), size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ft.Text("Versao", size=14, color=ft.Colors.GREY_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    expand=True,
                ),
            ])
            self.resultados_area.controls.append(cards)
            
            self.show_success("Estatisticas carregadas")
        except Exception as e:
            self.show_error(f"Erro: {str(e)}")
        self.page.update()
    
    def on_search_plant(self, e):
        planta = self.input_planta.value
        if not planta:
            self.show_error("Digite o nome da planta!")
            return
        
        self.show_loading(f"🔍 ANALISANDO: {planta.upper()}...")
        self.clear_results()
        self.page.update()
        
        def run_analysis():
            try:
                imagem_url = buscar_foto_wikipedia(planta)
                if imagem_url:
                    print(f"🖼️ URL da imagem: {imagem_url}")
                else:
                    print("🖼️ Imagem nao encontrada")
                
                from complant.main import analisar_planta as analisar
                resultados = analisar(planta, max_artigos=15)
                
                if resultados:
                    self.display_plant_results(planta, resultados, imagem_url)
                    self.show_success(f"{len(resultados)} compostos encontrados para {planta}")
                else:
                    self.show_error(f"Nenhum composto encontrado para {planta}")
            except Exception as e:
                self.show_error(f"Erro: {str(e)}")
                print(f"❌ Erro detalhado: {e}")
        
        threading.Thread(target=run_analysis).start()
    
    def on_search_compound(self, e):
        composto = self.input_composto.value
        if not composto:
            self.show_error("Digite o nome do composto!")
            return
        
        self.show_loading(f"🧪 BUSCANDO PLANTAS COM: {composto}...")
        self.clear_results()
        self.page.update()
        
        def run_analysis():
            try:
                from complant.main import buscar_plantas_por_composto as buscar
                plantas = buscar(composto, max_artigos=15)
                
                if plantas:
                    self.display_compound_results(composto, plantas)
                    self.show_success(f"{len(plantas)} plantas encontradas com {composto}")
                else:
                    self.show_error(f"Nenhuma planta encontrada com {composto}")
            except Exception as e:
                self.show_error(f"Erro: {str(e)}")
        
        threading.Thread(target=run_analysis).start()
    
    def on_categories(self, e):
        self.show_loading("📂 Carregando categorias...")
        self.display_categories()
        self.show_success("Categorias carregadas")
    
    def on_stats(self, e):
        self.show_loading("📊 Carregando estatisticas...")
        self.display_stats()
    
    def on_reload(self, e):
        self.show_loading("🔄 Recarregando banco de dados...")
        self.clear_results()
        
        try:
            if carregar_banco():
                self.show_success("Banco recarregado! 20.000 compostos")
            else:
                self.show_error("Erro ao recarregar banco")
        except Exception as e:
            self.show_error(f"Erro: {str(e)}")
        self.page.update()
    
    def build(self, page: ft.Page):
        self.page = page
        
        page.title = "🌿 COMPLANT - Analise Fitoquimica"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = ft.Colors.WHITE
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        
        VERDE = ft.Colors.GREEN_700
        VERDE_CLARO = ft.Colors.GREEN_50
        VERDE_ESCURO = ft.Colors.GREEN_900
        BRANCO = ft.Colors.WHITE
        PRETO = ft.Colors.BLACK
        CINZA = ft.Colors.GREY_700
        
        self.status_text = ft.Container(
            content=ft.Row([
                ft.Text("🔄", size=20),
                ft.Text("Carregando banco de dados...", size=14, color=CINZA),
            ]),
            padding=10,
            bgcolor=VERDE_CLARO,
            border_radius=8,
        )
        
        self.input_planta = ft.TextField(
            label="🔍 Nome da Planta",
            hint_text="Ex: Lippia alba",
            border_color=VERDE,
            width=400,
            on_submit=self.on_search_plant,
        )
        
        btn_planta = ft.Button(
            "🔍 Buscar Planta",
            bgcolor=VERDE,
            color=BRANCO,
            width=180,
            on_click=self.on_search_plant,
        )
        
        section_plant = ft.Container(
            content=ft.Column([
                ft.Text("🔍 BUSCAR POR PLANTA", size=16, weight=ft.FontWeight.BOLD, color=VERDE_ESCURO),
                ft.Row([self.input_planta, btn_planta], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text("Digite o nome da planta e veja seus compostos", size=12, color=CINZA),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=15,
            bgcolor=VERDE_CLARO,
            border_radius=10,
        )
        
        self.input_composto = ft.TextField(
            label="🧪 Nome do Composto",
            hint_text="Ex: quercetin",
            border_color=VERDE,
            width=400,
            on_submit=self.on_search_compound,
        )
        
        btn_composto = ft.Button(
            "🔍 Buscar Composto",
            bgcolor=PRETO,
            color=BRANCO,
            width=180,
            on_click=self.on_search_compound,
        )
        
        section_compound = ft.Container(
            content=ft.Column([
                ft.Text("🧪 BUSCAR POR COMPOSTO", size=16, weight=ft.FontWeight.BOLD, color=VERDE_ESCURO),
                ft.Row([self.input_composto, btn_composto], alignment=ft.MainAxisAlignment.CENTER),
                ft.Text("Digite o nome do composto e veja quais plantas o contem", size=12, color=CINZA),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=15,
            bgcolor=VERDE_CLARO,
            border_radius=10,
        )
        
        quick_buttons = ft.Row([
            ft.Button("📂 Categorias", bgcolor=VERDE, color=BRANCO, on_click=self.on_categories),
            ft.Button("📊 Estatisticas", bgcolor=VERDE, color=BRANCO, on_click=self.on_stats),
            ft.Button("🔄 Recarregar", bgcolor=PRETO, color=BRANCO, on_click=self.on_reload),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        
        self.resultados_area = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO)
        
        container_resultados = ft.Container(
            content=self.resultados_area,
            padding=15,
            bgcolor=BRANCO,
            border_radius=10,
        )
        
        footer = ft.Container(
            content=ft.Row([
                ft.Text("🌿 COMPLANT v1.0", size=12, color=CINZA),
                ft.Text("•", size=12, color=CINZA),
                ft.Text("20.000 compostos • 21 categorias", size=12, color=CINZA),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            padding=10,
        )
        
        page.add(
            ft.Text("🌿 COMPLANT", size=32, weight=ft.FontWeight.BOLD, color=VERDE_ESCURO),
            ft.Text("Analise Fitoquimica de Plantas", size=16, color=CINZA),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.status_text,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            section_plant,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            section_compound,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            quick_buttons,
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            container_resultados,
            footer,
        )
        
        if carregar_banco():
            self.show_success("Banco carregado! 20.000 compostos")
        else:
            self.show_error("Erro ao carregar banco")
        
        self.page.update()

if __name__ == "__main__":
    ft.app(target=lambda page: CompantApp().build(page))