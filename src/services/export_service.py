"""
Serviço responsável por exportações do sistema (Excel, PDF)
Independente de UI (puro Python)
"""
import os
import pandas as pd


class ExportService:
    """Serviço de Exportação desacoplado de interface gráfica"""
    
    @staticmethod
    def exportar_excel(df, arquivo):
        """Exporta um DataFrame para Excel com formatação de colunas"""
        if df is None or df.empty:
            raise ValueError("Não há dados para exportar.")
            
        with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados')
            worksheet = writer.sheets['Dados']
            for i, col in enumerate(df.columns):
                try:
                    val_len = df[col].astype(str).apply(len).max()
                except Exception:
                    val_len = 10
                max_len = max(val_len, len(str(col))) + 2
                worksheet.column_dimensions[chr(65 + (i % 26))].width = min(max_len, 50)
        return True

    @staticmethod
    def gerar_pdf(df, stats, arquivo):
        """Gera relatório PDF usando utils"""
        from src.utils import gerar_relatorio_pdf
        return gerar_relatorio_pdf(df, stats, arquivo)
