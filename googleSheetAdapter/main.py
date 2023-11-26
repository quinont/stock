from oauth2client.service_account import ServiceAccountCredentials
from fastapi import FastAPI, HTTPException
from datetime import datetime
import uvicorn
import gspread
import os

json_keyfile_name = os.environ.get("JSON_KEYFILE_NAME", "credentials.json")
sheet_key = os.environ.get("SHEET_KEY")


class GoogleSheetAdapter():
    def __init__(self, json_keyfile_name, sheet_key):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            json_keyfile_name
        )
        self.client = gspread.authorize(credentials)
        self.spreadsheet = self.client.open_by_key(sheet_key)

    # Falta mejorar este codigo.
    def actualizar_entrada_prediccion(self, id_pagina, fecha_hora):
        worksheet = self.spreadsheet.get_worksheet(id_pagina)

        last_row = len(worksheet.col_values(2)) + 1

        worksheet.update_cell(last_row, 2, fecha_hora)

        formula_fecha_a_epoch = f'=(B{last_row}-DATE(1970;1;1))*86400'
        worksheet.update_cell(last_row, 3, formula_fecha_a_epoch)
        worksheet.update_cell(last_row + 1, 1, last_row)

        formulaForecast = (
            f"=FORECAST(A{last_row + 1};"
            f"C{last_row - 6}:C{last_row};"
            f"A{last_row - 6}:A{last_row})"
        )
        worksheet.update_cell(last_row + 1, 8, formulaForecast)
        formulaEpocToDate = f"=EPOCHTODATE(H{last_row + 1})"
        worksheet.update_cell(last_row + 1, 9, formulaEpocToDate)

        estimacion = worksheet.cell(last_row + 1, 9).value

        return estimacion


app = FastAPI()
sheet_adapter = GoogleSheetAdapter(json_keyfile_name, sheet_key)


@app.get("/health")
def health_check():
    return {"status": "OK"}


@app.patch("/descontar/{product_id}/{cant}/")
def descontar_product(product_id: int, cant: int):
    try:
        now = datetime.now()
        fecha_hora_actual = now.strftime("%d/%m/%y %H:%M:%S")
        prediccion = sheet_adapter.actualizar_entrada_prediccion(
            2, fecha_hora_actual
        )
        return {"prediccion": f"{prediccion}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
