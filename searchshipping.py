from connection import *
from datetime import datetime, timedelta

def searchshipping(invoice):
    cols = {
        "numberinvoice": {
            "col": "CF.NUMERO_FACTURA",
            "val": invoice.numberinvoice
        },
        "numberbl": {
            "col": "DT.NUMERO_DOCUMENTO_TRANSPORTE",
            "val": invoice.numberbl
        },
        "datefrom": {
            "col": "CF.FECHA_FACTURA",
            "val": invoice.datefrom,
        },
        "dateto": {
            "col": "CF.FECHA_FACTURA",
            "val": invoice.dateto,
        }
    }

    filterwhere = []
    params = []
    if os.getenv("MODE") != "[DEMO]":
        try:
            if cols["numberinvoice"]["val"] not in (None, "string") and len(cols["numberinvoice"]["val"].strip()) > 0:
                filterwhere.append(cols["numberinvoice"]["col"] + " = %s")
                params.append(cols["numberinvoice"]["val"])
            if cols["numberbl"]["val"] not in (None, "string") and len(cols["numberbl"]["val"].strip()) > 0:
                filterwhere.append(cols["numberbl"]["col"] + " = %s")
                params.append(cols["numberbl"]["val"])
            if cols["datefrom"]["val"] not in (None, "string", "dd/mm/yyyy", "") and cols["dateto"]["val"] not in (None, "string", "dd/mm/yyyy", ""):
                if len(cols["datefrom"]["val"].strip()) > 0:
                    datefromDMY = datetime.strptime(cols["datefrom"]["val"], "%d/%m/%Y")
                    datetoDMY = datetime.strptime(cols["dateto"]["val"], "%d/%m/%Y")
                    filterwhere.append("CF.FECHA_FACTURA BETWEEN %s AND %s")
                    params.extend([datefromDMY.date(), datetoDMY.date()])
        except Exception as e:
            print(e)
            return {
                "error": "check dates, dd/mm/yyyy",
                "detail": str(e)
            }
    else:
        
        ...

    result = []
    if filterwhere:
        if os.getenv("MODE") != "[DEMO]":
            try:
                connection = goconnector()
                if connection.is_connected():
                    print("BD Connected")
                    sql = connection.cursor()
                    
                    query = """
                        SELECT
                            DATE_FORMAT(DT.FECHA_DOCUMENTO_TRANSPORTE, '%d/%m/%Y') AS FECHA_DOCUMENTO_TRANSPORTE,
                            DATE_FORMAT(VM.FECHA_ETA , '%d/%m/%Y') AS FECHA_ETA,
                            DATE_FORMAT(CF.FECHA_FACTURA, '%d/%m/%Y') AS FECHA_FACTURA,
                            DT.NUMERO_DOCUMENTO_TRANSPORTE,
                            CF.NUMERO_FACTURA,
                            FD.NUMERO_DEX,
                            DATE_FORMAT(FD.FECHA_DEX, '%d/%m/%Y') AS FECHA_DEX,
                            DATE_FORMAT(VM.FECHA_ETS, '%d/%m/%Y') AS FECHA_ETS,
                            COALESCE(DT.VALOR_FOB_USD,0) AS VALOR_FOB_USD,
                            COALESCE(DT.FLETE,0) AS FLETE,
                            DATE_FORMAT(FD.FECHA_ACEPTACION, '%d/%m/%Y') AS FECHA_ACEPTACION,
                            FD.NUMERO_ACEPTACION,
                            COALESCE(DT.VALOR_SEGUROS_USD,0) AS VALOR_SEGUROS_USD,
                            A.NOMBRE_ADMINISTRACION AS ADUANA_DESPACHO,
                            A.NOMBRE_ADMINISTRACION AS ADUANA_SALIDA,
                            'kg' AS CODIGO_UNIDAD_COMERCIAL,
                            MT.NOMBRE_MODO_TRANSPORTE AS MODO_TRANSPORTE,
                            'B' AS TIPO_DOCUMENTO_TRANSPORTE,
                            FD.NUMERO_DEX_CORRECCION,
                            DATE_FORMAT(FD.FECHA_DEX_CORRECCION, '%d/%m/%Y') AS FECHA_DEX_CORRECCION

                            FROM FACTURAS_EXPORTACIONES                       CF
                            LEFT OUTER JOIN EXPORTACIONES                     E  ON CF.NUMERO_DO=E.NUMERO_DO
                            LEFT OUTER JOIN ESTADOS_DO                        ED ON ED.NUMERO_DO=E.NUMERO_DO
                            LEFT OUTER JOIN DOCUMENTOS_TRANSPORTES_EXPOS      DT ON DT.NUMERO_DO=E.NUMERO_DO
                            LEFT OUTER JOIN EX_ADMINISTRACIONES               A  ON A.CODIGO_ADMINISTRACION=DT.CODIGO_ADMINISTRACION
                            LEFT OUTER JOIN VIAJES_MOTONAVES                  VM ON DT.ID_VIAJE_MOTONAVE=VM.ID_VIAJE_MOTONAVE
                            LEFT OUTER JOIN EX_SOLICITUDES_AUT_EMBARQUES      FD ON FD.NUMERO_DO=E.NUMERO_DO
                            LEFT OUTER JOIN DETALLES_FACTURAS_EXPO            DF ON DF.ID_FACTURA_EXPORTACION=CF.ID_FACTURA_EXPORTACION
                            LEFT OUTER JOIN EX_MODOS_TRANSPORTE               MT ON MT.CODIGO_MODO_TRANSPORTE=DT.CODIGO_MODO_TRANSPORTE
                            WHERE ED.ANULADO='N' AND ED.ID_IMPORTADOR='1578' {}
                        """.format(f" AND {filterwhere[0]}")
                    #print(query) show query
                    sql.execute(query, params)
                    
                    rows = sql.fetchall()
                    columns = [i[0] for i in sql.description]
                    for row in rows:
                        result.append(dict(zip(columns, row)))
                    if not rows:
                        result = {
                            "response": "03",
                            "message": "not found"
                        }
                    connection.close()
                    del connection
            except mysql.connector.Error as e:
                
                print(e)
                return {
                    "response": "00",
                    "message": "2003 (HY000): Can't connect to Data Base Server "
                }
                
        else:
            # Demo mode logic remains unchanged
            ...
    else:
        result = {
            "response": "04",
            "message": "no data input"
        }

    return result
