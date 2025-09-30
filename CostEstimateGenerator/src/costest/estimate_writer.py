"""
Write estimate outputs:
- Excel workbook with an 'Estimate' sheet:
    ITEM_CODE, DESCRIPTION, UNIT, QUANTITY,
    UNIT_PRICE_EST plus category price/count columns,
    EXTENDED (QUANTITY * UNIT_PRICE_EST),
    SOURCE, NOTES
- 'Summary' sheet with subtotal
- CSV audit file with all columns
- Conditional formatting: highlight UNIT_PRICE_EST == 0
- Auto-fit column widths
- TOTAL cell at bottom of EXTENDED column (bold, currency)
"""

from __future__ import annotations

import os
import re
import json
import pandas as pd
import numpy as np

from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo

ZERO_FILL = PatternFill(start_color="FFF9C4", end_color="FFF9C4", fill_type="solid")  # pale yellow
PRICING_FILL = PatternFill(start_color="C8E6C9", end_color="C8E6C9", fill_type="solid")  # pale green
ALTERNATE_FILL = PatternFill(start_color="F8BBD0", end_color="F8BBD0", fill_type="solid")  # light red

CATEGORY_PRICE_COLS = [
    "DIST_12M_PRICE",
    "DIST_24M_PRICE",
    "DIST_36M_PRICE",
    "STATE_12M_PRICE",
    "STATE_24M_PRICE",
    "STATE_36M_PRICE",
]

CATEGORY_COUNT_COLS = [
    "DIST_12M_COUNT",
    "DIST_24M_COUNT",
    "DIST_36M_COUNT",
    "STATE_12M_COUNT",
    "STATE_24M_COUNT",
    "STATE_36M_COUNT",
]

CATEGORY_INCLUDED_COLS = [
    "DIST_12M_INCLUDED",
    "DIST_24M_INCLUDED",
    "DIST_36M_INCLUDED",
    "STATE_12M_INCLUDED",
    "STATE_24M_INCLUDED",
    "STATE_36M_INCLUDED",
]



def _format_and_save_excel(df: pd.DataFrame, xlsx_path: str):
    out = df.copy()
    out.drop(columns=['CONFIDENCE', 'STD_DEV', 'COEF_VAR', 'N_FOR_CONF'], errors='ignore', inplace=True)
    for col in CATEGORY_INCLUDED_COLS:
        if col not in out.columns:
            out[col] = False
    if 'ALTERNATE_USED' not in out.columns:
        out['ALTERNATE_USED'] = False
    out["EXTENDED"] = out["QUANTITY"].astype(float) * out["UNIT_PRICE_EST"].astype(float)

    alt_flag = out['ALTERNATE_USED'].fillna(False) if 'ALTERNATE_USED' in out.columns else pd.Series(False, index=out.index)
    alt_related_cols = [
        "ALTERNATE_USED", "ALTERNATE_SOURCE_ITEM", "ALTERNATE_RATIO",
        "ALTERNATE_BASE_PRICE", "ALTERNATE_SOURCE_AREA", "ALTERNATE_CANDIDATE_COUNT",
        "ALTERNATE_METHOD", "ALTERNATE_AI_NOTES",
        "GEOM_SHAPE", "GEOM_AREA_SQFT", "GEOM_DIMENSIONS",
    ]
    alt_seek_df = pd.DataFrame()
    if 'ALTERNATE_USED' in out.columns:
        alt_seek_df = out[out['ALTERNATE_USED'].fillna(False)].copy()
        alt_seek_columns = [
            "ITEM_CODE", "DESCRIPTION", "UNIT", "QUANTITY",
            "UNIT_PRICE_EST", "EXTENDED", "DATA_POINTS_USED",
            "GEOM_SHAPE", "GEOM_AREA_SQFT", "GEOM_DIMENSIONS",
            "ALTERNATE_SOURCE_ITEM", "ALTERNATE_RATIO",
            "ALTERNATE_BASE_PRICE", "ALTERNATE_SOURCE_AREA",
            "ALTERNATE_CANDIDATE_COUNT", "ALT_TOTAL_CANDIDATES",
            "ALT_SELECTED_COUNT", "ALT_SCORE_OVERALL", "ALT_SCORE_GEOMETRY",
            "ALT_SCORE_SPEC", "ALT_SCORE_RECENCY", "ALT_SCORE_LOCALITY",
            "ALT_SCORE_DATA_VOLUME", "ALT_SIMILARITY_NOTES",
            "ALT_SHOW_WORK_METHOD", "ALTERNATE_METHOD",
            "ALTERNATE_AI_NOTES", "NOTES",
        ]
        if not alt_seek_df.empty:
            alt_seek_df = alt_seek_df[[col for col in alt_seek_columns if col in alt_seek_df.columns]]
    out = out.drop(columns=alt_related_cols, errors='ignore')
    if len(out) != len(alt_flag):
        alt_flag = alt_flag.reindex(out.index, fill_value=False)
    out['ALT_FLAG'] = alt_flag.values

    cols = [
        "ITEM_CODE", "DESCRIPTION", "UNIT", "QUANTITY",
        "UNIT_PRICE_EST", "EXTENDED", "DATA_POINTS_USED",
    ] + CATEGORY_PRICE_COLS + CATEGORY_COUNT_COLS + CATEGORY_INCLUDED_COLS + [
        "NOTES", "ALT_FLAG"
    ]
    cols = [c for c in cols if c in out.columns] + [c for c in out.columns if c not in cols]
    out = out[cols]

    os.makedirs(os.path.dirname(xlsx_path), exist_ok=True)
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as xlw:
        out.to_excel(xlw, sheet_name="Estimate", index=False)
        if not alt_seek_df.empty:
            alt_seek_df.to_excel(xlw, sheet_name="Alt-Seek", index=False)
        ws = xlw.sheets["Estimate"]
        ws.freeze_panes = "A2"

        headers = [cell.value for cell in ws[1]]
        data_start_row = 2
        data_end_row = ws.max_row

        header_fill = PatternFill(start_color="1E3A5F", end_color="1E3A5F", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font

        currency_cols = set(CATEGORY_PRICE_COLS) | {"UNIT_PRICE_EST", "EXTENDED"}
        integer_cols = set(CATEGORY_COUNT_COLS) | {"DATA_POINTS_USED"}
        right_align = Alignment(horizontal='right')

        if data_end_row >= data_start_row:
            last_col_letter = get_column_letter(ws.max_column)
            table = Table(displayName="EstimateTable", ref=f"A1:{last_col_letter}{data_end_row}")
            table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True, showColumnStripes=False)
            ws.add_table(table)

        for col_name in headers:
            col_idx = headers.index(col_name) + 1
            if col_name in currency_cols:
                for row_idx in range(data_start_row, data_end_row + 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.number_format = '$#,##0.00'
                    cell.alignment = right_align
            elif col_name in integer_cols:
                for row_idx in range(data_start_row, data_end_row + 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.number_format = '0'
                    cell.alignment = right_align

        if "UNIT_PRICE_EST" in headers and data_end_row >= data_start_row:
            idx = headers.index("UNIT_PRICE_EST") + 1
            col_letter = get_column_letter(idx)
            rng = f"{col_letter}{data_start_row}:{col_letter}{data_end_row}"
            ws.conditional_formatting.add(
                rng,
                CellIsRule(operator="equal", formula=["0"], fill=ZERO_FILL)
            )

        if "EXTENDED" in headers and data_end_row >= data_start_row:
            ext_idx = headers.index("EXTENDED") + 1
            ext_letter = get_column_letter(ext_idx)
            total_row = data_end_row + 1
            label_cell = ws.cell(row=total_row, column=max(1, ext_idx - 1))
            label_cell.value = "TOTAL"
            label_cell.font = Font(bold=True)
            label_cell.alignment = Alignment(horizontal='right')

            total_cell = ws.cell(row=total_row, column=ext_idx)
            total_cell.value = f"=SUM({ext_letter}{data_start_row}:{ext_letter}{data_end_row})"
            total_cell.font = Font(bold=True)
            total_cell.number_format = '$#,##0.00'

        data_end_cf = data_end_row
        if ws.max_row > data_end_row:
            last_row_cells = list(ws[ws.max_row])
            if any(isinstance(cell.value, str) and cell.value.strip().upper() == "TOTAL" for cell in last_row_cells):
                data_end_cf = ws.max_row - 1

        for include_col, price_col, count_col in zip(CATEGORY_INCLUDED_COLS, CATEGORY_PRICE_COLS, CATEGORY_COUNT_COLS):
            if include_col not in headers:
                continue
            include_idx = headers.index(include_col) + 1
            include_letter = get_column_letter(include_idx)
            ws.column_dimensions[include_letter].hidden = True
            if data_end_cf < data_start_row:
                continue
            formula = f"=${include_letter}{data_start_row}"
            if price_col in headers:
                price_idx = headers.index(price_col) + 1
                price_letter = get_column_letter(price_idx)
                rng = f"{price_letter}{data_start_row}:{price_letter}{data_end_cf}"
                ws.conditional_formatting.add(
                    rng,
                    FormulaRule(formula=[formula], fill=PRICING_FILL, stopIfTrue=False),
                )

        if "ALT_FLAG" in headers:
            alt_idx = headers.index("ALT_FLAG") + 1
            alt_letter = get_column_letter(alt_idx)
            ws.column_dimensions[alt_letter].hidden = True
            if data_end_cf >= data_start_row:
                formula = f"=${alt_letter}{data_start_row}"
                for target_col in ("ITEM_CODE", "UNIT_PRICE_EST"):
                    if target_col in headers:
                        tgt_idx = headers.index(target_col) + 1
                        tgt_letter = get_column_letter(tgt_idx)
                        rng = f"{tgt_letter}{data_start_row}:{tgt_letter}{data_end_cf}"
                        ws.conditional_formatting.add(
                            rng,
                            FormulaRule(formula=[formula], fill=ALTERNATE_FILL, stopIfTrue=False),
                        )

        for col_idx, col in enumerate(ws.iter_cols(1, ws.max_column), start=1):
            header_name = headers[col_idx - 1] if col_idx - 1 < len(headers) else None
            if header_name == "ALT_FLAG":
                continue
            max_len = max((len(str(cell.value)) if cell.value is not None else 0) for cell in col)
            ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 2, 60)

        if not alt_seek_df.empty:
            ws_alt = xlw.sheets["Alt-Seek"]
            ws_alt.freeze_panes = "A2"

            header_fill_alt = PatternFill(start_color="1E3A5F", end_color="1E3A5F", fill_type="solid")
            header_font_alt = Font(color="FFFFFF", bold=True)
            for cell in ws_alt[1]:
                cell.fill = header_fill_alt
                cell.font = header_font_alt

            alt_headers = [cell.value for cell in ws_alt[1]]
            for col_name in alt_headers:
                col_idx = alt_headers.index(col_name) + 1
                if col_name in currency_cols:
                    for row_idx in range(2, ws_alt.max_row + 1):
                        cell = ws_alt.cell(row=row_idx, column=col_idx)
                        cell.number_format = '$#,##0.00'
                        cell.alignment = right_align
                elif col_name in integer_cols:
                    for row_idx in range(2, ws_alt.max_row + 1):
                        cell = ws_alt.cell(row=row_idx, column=col_idx)
                        cell.number_format = '0'
                        cell.alignment = right_align

            for column_cells in ws_alt.columns:
                values = [str(cell.value) for cell in column_cells if cell.value is not None]
                max_len = max((len(value) for value in values), default=0)
                ws_alt.column_dimensions[column_cells[0].column_letter].width = min(max_len + 2, 60)


def _safe_sheet_name(name: str, existing: set[str]) -> str:
    base = str(name).strip() or "ITEM"
    base = re.sub(r"[\\/*?:\[\]]", "_", base)
    base = base or "ITEM"
    base = base[:31]
    candidate = base
    counter = 1
    while candidate.upper() in existing:
        suffix = f"_{counter}"
        if len(base) + len(suffix) > 31:
            candidate = base[: 31 - len(suffix)] + suffix
        else:
            candidate = base + suffix
        counter += 1
    existing.add(candidate.upper())
    return candidate


def _write_payitem_audit(payitem_details: dict[str, pd.DataFrame], audit_path: str) -> None:
    if not audit_path:
        return

    folder = os.path.dirname(audit_path) or "."
    os.makedirs(folder, exist_ok=True)

    details = payitem_details or {}
    with pd.ExcelWriter(audit_path, engine="openpyxl") as xlw:
        used_names: set[str] = set()

        if not details:
            placeholder = pd.DataFrame(
                [{"MESSAGE": "No pay items available in the current estimate."}]
            )
            placeholder.to_excel(xlw, sheet_name="PayItems", index=False)
            ws = xlw.sheets["PayItems"]
            if ws.max_row > 1:
                ws.freeze_panes = "A2"
            for col_idx, col in enumerate(ws.iter_cols(1, ws.max_column), start=1):
                max_len = 0
                for cell in col:
                    val = "" if cell.value is None else str(cell.value)
                    if len(val) > max_len:
                        max_len = len(val)
                ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 2, 60)
            return

        for item_code, detail in details.items():
            sheet_name = _safe_sheet_name(item_code, used_names)
            data = detail.copy()

            if data.empty:
                data = pd.DataFrame(
                    [{"MESSAGE": "No BidTabs history found for this pay item."}]
                )
                data.to_excel(xlw, sheet_name=sheet_name, index=False)
                ws = xlw.sheets[sheet_name]
            else:
                if "LETTING_DATE" in data.columns:
                    data["LETTING_DATE"] = pd.to_datetime(data["LETTING_DATE"], errors="coerce")
                data.to_excel(xlw, sheet_name=sheet_name, index=False)
                ws = xlw.sheets[sheet_name]

            if ws.max_row > 1:
                ws.freeze_panes = "A2"

            headers = [cell.value for cell in ws[1]]
            if "USED_FOR_PRICING" in headers:
                idx = headers.index("USED_FOR_PRICING") + 1
                col_letter = get_column_letter(idx)
                data_start_row = 2
                last_data_row = ws.max_row
                if last_data_row >= data_start_row:
                    ws.conditional_formatting.add(
                        f"{col_letter}{data_start_row}:{col_letter}{last_data_row}",
                        CellIsRule(operator="equal", formula=["TRUE"], fill=PRICING_FILL),
                    )

            for col_idx, col in enumerate(ws.iter_cols(1, ws.max_column), start=1):
                max_len = 0
                for cell in col:
                    val = "" if cell.value is None else str(cell.value)
                    if len(val) > max_len:
                        max_len = len(val)
                ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 2, 60)



def write_outputs(
    df: pd.DataFrame,
    xlsx_path: str,
    audit_csv_path: str,
    payitem_details: dict[str, pd.DataFrame] | None = None,
    payitem_audit_path: str | None = None,
) -> None:
    # If payitem_details not provided, try to load from payitem_audit_path (existing workbook)
    if not payitem_details and payitem_audit_path:
        try:
            loaded = pd.read_excel(payitem_audit_path, sheet_name=None, engine='openpyxl')
            # convert sheet dict to same form as expected
            payitem_details = {str(k): v for k, v in (loaded or {}).items()}
        except Exception:
            payitem_details = None

    # Compute per-item historical statistics from payitem_details (if provided)
    stats = {}
    if payitem_details:
        for item_code, detail in (payitem_details or {}).items():
            try:
                d = detail.copy()
                # Normalize column names to strings
                d.columns = [str(c) for c in d.columns]
                # Try to detect a unit price column if 'UNIT_PRICE' not present
                price_col = None
                for col in d.columns:
                    if re.search(r"^unit[_ ]?price$", col, re.I):
                        price_col = col
                        break
                if price_col is None:
                    # fallback: any column containing 'price'
                    for col in d.columns:
                        if 'price' in col.lower():
                            price_col = col
                            break
                if price_col is not None:
                    d[price_col] = pd.to_numeric(d[price_col], errors='coerce')
                    prices = d[price_col].dropna()
                    n = int(prices.count())
                    mean_hist = float(prices.mean()) if n > 0 else float('nan')
                    std_hist = float(prices.std(ddof=0)) if n > 0 else float('nan')
                else:
                    n = 0
                    mean_hist = float('nan')
                    std_hist = float('nan')
                cv = float('inf')
                if not pd.isna(mean_hist) and mean_hist != 0:
                    cv = abs(std_hist / mean_hist) if not pd.isna(std_hist) else float('inf')
                # store stats under the original key
                stats[str(item_code)] = {
                    'STD_DEV': std_hist,
                    'COEF_VAR': cv,
                    'N_SAMPLES': n,
                }
                # also store under a sanitized key to match sheet-name variants
                try:
                    sane = re.sub(r"[\\/*?:\[\]]", "_", str(item_code)).strip()
                    sane = sane[:31]
                    if sane and sane not in stats:
                        stats[sane] = stats[str(item_code)]
                except Exception:
                    pass
            except Exception:
                stats[str(item_code)] = {'STD_DEV': float('nan'), 'COEF_VAR': float('inf'), 'N_SAMPLES': 0}

    # Dump stats for debugging so we can inspect mapping externally
    try:
        os.makedirs('outputs', exist_ok=True)
        dump = {}
        for k, v in stats.items():
            dump[str(k)] = {
                'STD_DEV': None if (v.get('STD_DEV') is None or pd.isna(v.get('STD_DEV'))) else float(v.get('STD_DEV')),
                'COEF_VAR': None if (v.get('COEF_VAR') is None or pd.isna(v.get('COEF_VAR')) or str(v.get('COEF_VAR')) in ('inf', 'nan')) else float(v.get('COEF_VAR')),
                'N_SAMPLES': int(v.get('N_SAMPLES') or 0),
            }
        with open('outputs/payitem_stats_debug.json', 'w', encoding='utf-8') as fh:
            json.dump(dump, fh, indent=2)
    except Exception:
        pass

    # Merge computed stats into a working copy of df so we can compute CONFIDENCE
    work = df.copy()
    work['ITEM_CODE'] = work['ITEM_CODE'].astype(str)
    # helper to try multiple key representations when looking up stats
    def _normalize(k: str) -> str:
        return re.sub(r"[^A-Za-z0-9]", "", str(k)).strip().upper()

    def _lookup_stat(code, key_name):
        if code is None:
            return None
        code_s = str(code)
        # direct match
        s = stats.get(code_s)
        if s and key_name in s and s.get(key_name) is not None:
            return s.get(key_name)
        # sanitized exact match (sheet-safe)
        try:
            sane = re.sub(r"[\\/*?:\[\]]", "_", code_s).strip()[:31]
            s2 = stats.get(sane)
            if s2 and key_name in s2 and s2.get(key_name) is not None:
                return s2.get(key_name)
        except Exception:
            pass
        # case variants
        s3 = stats.get(code_s.upper()) or stats.get(code_s.lower())
        if s3 and key_name in s3 and s3.get(key_name) is not None:
            return s3.get(key_name)
        # normalized alphanumeric match
        norm = _normalize(code_s)
        for kstat, vstat in stats.items():
            try:
                if _normalize(kstat) == norm and key_name in vstat and vstat.get(key_name) is not None:
                    return vstat.get(key_name)
            except Exception:
                continue
        # substring contains
        for kstat, vstat in stats.items():
            try:
                if str(code_s) in str(kstat) and key_name in vstat and vstat.get(key_name) is not None:
                    return vstat.get(key_name)
            except Exception:
                continue
        return None

    work['STD_DEV'] = work['ITEM_CODE'].map(lambda c: _lookup_stat(c, 'STD_DEV'))
    work['COEF_VAR'] = work['ITEM_CODE'].map(lambda c: _lookup_stat(c, 'COEF_VAR'))

    # Fallback: if STD_DEV/COEF_VAR are missing, compute from available category price columns in the estimate row
    try:
        price_cols = [c for c in CATEGORY_PRICE_COLS if c in work.columns]
        if price_cols:
            def _row_price_stats(row):
                vals = []
                for pc in price_cols:
                    try:
                        v = float(row.get(pc))
                        if not pd.isna(v):
                            vals.append(v)
                    except Exception:
                        continue
                if not vals:
                    return pd.Series({'STD_DEV_fallback': pd.NA, 'COEF_VAR_fallback': pd.NA})
                import math
                mean = sum(vals) / len(vals)
                if len(vals) > 1:
                    # population std (ddof=0)
                    s2 = sum((x - mean) ** 2 for x in vals) / len(vals)
                    std = math.sqrt(s2)
                else:
                    std = 0.0
                cv = float('inf')
                if mean != 0:
                    cv = abs(std / mean)
                return pd.Series({'STD_DEV_fallback': std, 'COEF_VAR_fallback': cv})

            fallbacks = work.apply(_row_price_stats, axis=1)
            # Where original STD_DEV is null, fill from fallback
            work['STD_DEV'] = work['STD_DEV'].combine_first(fallbacks['STD_DEV_fallback'])
            work['COEF_VAR'] = work['COEF_VAR'].combine_first(fallbacks['COEF_VAR_fallback'])
    except Exception:
        pass

    # Finalize: ensure numeric types and fill missing values so they appear in CSV
    try:
        work['STD_DEV'] = pd.to_numeric(work['STD_DEV'], errors='coerce')
    except Exception:
        pass
    try:
        work['COEF_VAR'] = pd.to_numeric(work['COEF_VAR'], errors='coerce')
    except Exception:
        pass
    # Fill missing STD_DEV with 0.0 (no variation) and COEF_VAR with inf so confidence computes to 0
    work['STD_DEV'] = work['STD_DEV'].fillna(0.0)
    # For COEF_VAR, use a large number to represent unknown/very high variance
    work['COEF_VAR'] = work['COEF_VAR'].fillna(float('inf'))

    # Determine sample count to use: prefer DATA_POINTS_USED (if present), else N_SAMPLES
    def _get_n(row):
        try:
            n = int(row.get('DATA_POINTS_USED') or 0)
            if n > 0:
                return n
        except Exception:
            pass
        # fallback to N_SAMPLES from stats
        try:
            return int(stats.get(str(row.get('ITEM_CODE')), {}).get('N_SAMPLES', 0) or 0)
        except Exception:
            return 0

    work['N_FOR_CONF'] = work.apply(_get_n, axis=1)

    # Compute confidence: (1 - exp(-n/30)) * (1 / (1 + cv))
    import math

    def _compute_conf(row):
        n = row.get('N_FOR_CONF') or 0
        cv = row.get('COEF_VAR')
        try:
            if cv is None or pd.isna(cv) or math.isinf(float(cv)):
                return 0.0
            factor_n = 1.0 - math.exp(-float(n) / 30.0)
            factor_cv = 1.0 / (1.0 + float(cv))
            val = float(max(0.0, min(1.0, factor_n * factor_cv)))
            return val
        except Exception:
            return 0.0

    work['CONFIDENCE'] = work.apply(_compute_conf, axis=1)

    # Write mapping debug file showing which stats key (if any) matched each item
    try:
        dbg_rows = []
        for _, row in work[['ITEM_CODE', 'STD_DEV', 'COEF_VAR', 'N_FOR_CONF']].iterrows():
            dbg_rows.append({
                'ITEM_CODE': row.get('ITEM_CODE'),
                'STD_DEV': None if pd.isna(row.get('STD_DEV')) else float(row.get('STD_DEV')),
                'COEF_VAR': None if pd.isna(row.get('COEF_VAR')) or str(row.get('COEF_VAR')) in ('inf', 'nan') else float(row.get('COEF_VAR')),
                'N_FOR_CONF': int(row.get('N_FOR_CONF') or 0),
            })
        import csv
        with open(os.path.join('outputs', 'payitem_mapping_debug.csv'), 'w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=['ITEM_CODE', 'STD_DEV', 'COEF_VAR', 'N_FOR_CONF'])
            writer.writeheader()
            for r in dbg_rows:
                writer.writerow(r)
    except Exception:
        pass

        # (debug prints removed)

    # Prepare Excel DataFrame: include CONFIDENCE but exclude STD_DEV/COEF_VAR (user requested only CONFIDENCE in Estimate_Draft)
    excel_df = work.copy()
    # Ensure CONFIDENCE comes after DATA_POINTS_USED by reordering if necessary
    if 'DATA_POINTS_USED' in excel_df.columns:
        cols = list(excel_df.columns)
        # remove CONFIDENCE if present then insert after DATA_POINTS_USED
        if 'CONFIDENCE' in cols:
            cols.remove('CONFIDENCE')
        idx = cols.index('DATA_POINTS_USED') + 1
        cols.insert(idx, 'CONFIDENCE')
        excel_df = excel_df[cols]

    # Excel with numeric prices only, zero-highlighting, total cell, auto-fit
    _format_and_save_excel(excel_df, xlsx_path)

    # CSV audit: full details including STD_DEV and COEF_VAR
    os.makedirs(os.path.dirname(audit_csv_path), exist_ok=True)
    csv_df = work.drop(columns=CATEGORY_INCLUDED_COLS, errors='ignore')
    # Move STD_DEV and COEF_VAR to appear after DATA_POINTS_USED in the CSV
    if 'DATA_POINTS_USED' in csv_df.columns:
        cols = list(csv_df.columns)
        # remove if present
        for extra in ('STD_DEV', 'COEF_VAR'):
            if extra in cols:
                cols.remove(extra)
        idx = cols.index('DATA_POINTS_USED') + 1
        for i, extra in enumerate(('STD_DEV', 'COEF_VAR')):
            cols.insert(idx + i, extra)
        csv_df = csv_df[cols]
    # Ensure numeric STD_DEV/COEF_VAR are present in the CSV
    try:
        csv_df['STD_DEV'] = pd.to_numeric(csv_df.get('STD_DEV'), errors='coerce').fillna(0.0)
    except Exception:
        csv_df['STD_DEV'] = 0.0
    try:
        csv_df['COEF_VAR'] = pd.to_numeric(csv_df.get('COEF_VAR'), errors='coerce')
        # Replace infinite variance with a large sentinel so CSV shows a value
        csv_df['COEF_VAR'].replace([np.inf, -np.inf], 1e9, inplace=True)
        csv_df['COEF_VAR'] = csv_df['COEF_VAR'].fillna(1e9)
    except Exception:
        csv_df['COEF_VAR'] = 1e9

    # Add human-readable string columns so values are visible in CSV/Excel viewers
    try:
        def fmt_std(v):
            try:
                if v is None:
                    return 'N/A'
                if float(v) >= 1e8:
                    return 'N/A'
                return f"{float(v):.2f}"
            except Exception:
                return 'N/A'

        def fmt_cv(v):
            try:
                if v is None:
                    return 'N/A'
                fv = float(v)
                if fv >= 1e8 or fv == float('inf'):
                    return 'N/A'
                return f"{fv:.4f}"
            except Exception:
                return 'N/A'

        csv_df['STD_DEV_STR'] = csv_df['STD_DEV'].apply(fmt_std)
        csv_df['COEF_VAR_STR'] = csv_df['COEF_VAR'].apply(fmt_cv)
    except Exception:
        csv_df['STD_DEV_STR'] = ''
        csv_df['COEF_VAR_STR'] = ''

    # Reorder to place the string columns after the numeric ones for visibility
    try:
        if 'STD_DEV' in csv_df.columns and 'COEF_VAR' in csv_df.columns:
            cols = list(csv_df.columns)
            # remove any existing string cols then insert after COEF_VAR
            for extra in ('STD_DEV_STR', 'COEF_VAR_STR'):
                if extra in cols:
                    cols.remove(extra)
            idx = cols.index('COEF_VAR') + 1
            cols.insert(idx, 'STD_DEV_STR')
            cols.insert(idx + 1, 'COEF_VAR_STR')
            csv_df = csv_df[cols]
    except Exception:
        pass

    export_df = csv_df.drop(columns=['STD_DEV', 'COEF_VAR', 'STD_DEV_STR', 'COEF_VAR_STR', 'N_FOR_CONF', 'CONFIDENCE'], errors='ignore')
    export_df.to_csv(audit_csv_path, index=False)

    # Also write a small debug CSV with key computed columns so it's easy to inspect
    try:
        dbg_cols = [c for c in ['ITEM_CODE', 'DATA_POINTS_USED', 'STD_DEV', 'COEF_VAR', 'N_FOR_CONF', 'CONFIDENCE', 'STD_DEV_STR', 'COEF_VAR_STR'] if c in csv_df.columns]
        dbg_df = csv_df[dbg_cols].copy()
        dbg_path = os.path.join('outputs', 'debug_compute_stats.csv')
        dbg_df.to_csv(dbg_path, index=False)
    except Exception:
        pass

    if payitem_audit_path:
        _write_payitem_audit(payitem_details or {}, payitem_audit_path)


