// ============================================================
//  Qikify QA — Google Apps Script v3
//  Cách dùng:
//  1. Script tự tạo sheet "📥 Claude Import" khi lần đầu chạy
//  2. Paste JSON từ Claude vào ô B1 của sheet đó
//  3. Vào menu 🧪 Qikify QA → Import Test Cases từ Claude
//
//  v3 (2026-08-13): thêm 2 cột "Execution Type" và "Automation Script Ref".
//  Khi append vào tab tạo bởi bản v2 (11 cột), script map dữ liệu theo TÊN cột
//  chứ không theo vị trí, và hỏi user có bổ sung 2 cột mới vào cuối tab không.
// ============================================================

const IMPORT_SHEET_NAME = '📥 Claude Import';

const APP_TAB_COLORS = {
  TEPO: '#4472C4',
  QSC:  '#70AD47',
  QCO:  '#000000',
  // QCC là mã cũ của Checkout Customizer, khai tử 2026-08-12 (giờ dùng QCO cho
  // cả project key lẫn test case prefix). Giữ lại để các tab [QCC] … đã có trên
  // Master Sheet không bị đổi sang màu xám mặc định khi append.
  QCC:  '#000000',
  DUOS: '#ED7D31',
  MTRO: '#4f117e',
  XAP:  '#C7387A',
};

const STATUS_COLORS = {
  'Pending':       '#F2F2F2',
  'Assign to DEV': '#bfe1f6',
  'Ready to test': '#ffe5a0',
  'Pass':          '#E2EFDA',
  'Fail':          '#FFDCE1',
  'Reopen':        '#e6cff2',
};

const STATUS_VALUES = ['Pending', 'Assign to DEV', 'Ready to test', 'Pass', 'Fail', 'Reopen'];

const EXECUTION_TYPE_VALUES = ['Automated', 'Manual', 'To be automated'];

const EXECUTION_TYPE_COLORS = {
  'Automated':       '#D9EAD3',
  'Manual':          '#FFF2CC',
  'To be automated': '#D0E2F3',
};

const HEADERS = [
  'Test Case ID', 'Module', 'Test Scenario', 'Priority',
  'Preconditions', 'Steps', 'Data', 'Expected Result',
  'Status', 'Actual Result', 'Notes',
  'Execution Type', 'Automation Script Ref'
];

const COLUMN_WIDTHS = {
  'Test Case ID':          120,
  'Module':                220,
  'Test Scenario':         300,
  'Priority':               90,
  'Preconditions':         280,
  'Steps':                 360,
  'Data':                  100,
  'Expected Result':       360,
  'Status':                 90,
  'Actual Result':         150,
  'Notes':                 150,
  'Execution Type':        120,
  'Automation Script Ref': 220,
};

// ── TẠO SHEET IMPORT NẾU CHƯA CÓ ────────────────────────────
function ensureImportSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let ws = ss.getSheetByName(IMPORT_SHEET_NAME);
  if (!ws) {
    ws = ss.insertSheet(IMPORT_SHEET_NAME);
    ws.setTabColor('#CCCCCC');

    // Hướng dẫn ở cột A
    ws.getRange('A1').setValue('Paste JSON từ Claude vào ô B1 →')
      .setFontWeight('bold')
      .setFontColor('#1F4E79');
    ws.getRange('A2').setValue('Sau đó vào menu 🧪 Qikify QA → Import Test Cases từ Claude')
      .setFontColor('#666666')
      .setFontSize(10);

    ws.setColumnWidth(1, 280);
    ws.setColumnWidth(2, 600);

    // Highlight ô B1 để dễ nhận ra
    ws.getRange('B1')
      .setBackground('#FFF2CC')
      .setBorder(true, true, true, true, false, false, '#ED7D31', SpreadsheetApp.BorderStyle.SOLID_MEDIUM);
  }
  return ws;
}

// ── HÀM CHÍNH ────────────────────────────────────────────────
function pushTestCases() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();

  // Đảm bảo import sheet tồn tại
  const importSheet = ensureImportSheet_();

  // Đọc JSON từ ô B1
  const raw = importSheet.getRange('B1').getValue().toString().trim();

  if (!raw) {
    // Chuyển sang sheet import để user biết paste vào đâu
    ss.setActiveSheet(importSheet);
    importSheet.getRange('B1').activate();
    ui.alert(
      '⚠️ Chưa có dữ liệu',
      'Paste JSON từ Claude vào ô B1 của sheet "' + IMPORT_SHEET_NAME + '" rồi chạy lại.',
      ui.ButtonSet.OK
    );
    return;
  }

  // Parse JSON
  let payload;
  try {
    payload = JSON.parse(raw);
  } catch (e) {
    ss.setActiveSheet(importSheet);
    ui.alert('❌ JSON không hợp lệ', 'Kiểm tra lại nội dung ô B1.\n\nLỗi: ' + e.message, ui.ButtonSet.OK);
    return;
  }

  const { sheetName, appPrefix, featureTitle, testCases } = payload;

  if (!sheetName || !appPrefix || !testCases || !testCases.length) {
    ui.alert('❌ Thiếu trường', 'JSON cần có: sheetName, appPrefix, testCases', ui.ButtonSet.OK);
    return;
  }

  // Lấy hoặc tạo sheet đích
  let ws = ss.getSheetByName(sheetName);
  let isNew = false;
  if (!ws) {
    ws = ss.insertSheet(sheetName);
    isNew = true;
    ws.setTabColor(APP_TAB_COLORS[appPrefix.toUpperCase()] || '#888888');
  }

  // Bộ cột dùng để ghi: tab mới dùng HEADERS chuẩn; tab cũ dùng đúng header đang có
  // trên sheet (map theo TÊN cột, không theo vị trí) để các tab tạo từ bản script cũ
  // vẫn append được mà không lệch cột.
  let headers;
  if (isNew) {
    writeHeaderRows_(ws, featureTitle || sheetName);
    headers = HEADERS.slice();
  } else {
    headers = resolveHeaders_(ws, ui);
  }

  const startRow = Math.max(ws.getLastRow(), 2) + 1;
  writeDataRows_(ws, testCases, startRow, headers);

  // Xóa ô B1 sau khi import xong
  importSheet.getRange('B1').clearContent();

  // Chuyển sang sheet vừa tạo
  ss.setActiveSheet(ws);

  ui.alert('✅ Xong!', 'Đã ghi ' + testCases.length + ' test cases vào sheet "' + sheetName + '".', ui.ButtonSet.OK);
}

// ── HEADER CỦA TAB ĐÃ TỒN TẠI ─────────────────────────────────
// Đọc header thật đang có ở row 2. Nếu thiếu cột nào so với HEADERS chuẩn
// (tab tạo từ bản script cũ, chưa có Execution Type / Automation Script Ref),
// hỏi user có bổ sung vào cuối tab không — không tự ý sửa sheet đang có data.
function resolveHeaders_(ws, ui) {
  const lastCol = ws.getLastColumn();
  if (lastCol < 1) return HEADERS.slice();

  const existing = ws.getRange(2, 1, 1, lastCol).getDisplayValues()[0]
    .map(function(h) { return h.toString().trim(); });
  while (existing.length && !existing[existing.length - 1]) existing.pop();

  // Không nhận ra là tab test case chuẩn → dùng bộ cột chuẩn, đừng đoán thêm
  if (existing.indexOf('Test Case ID') === -1) return HEADERS.slice();

  const missing = HEADERS.filter(function(h) { return existing.indexOf(h) === -1; });
  if (!missing.length) return existing;

  const resp = ui.alert(
    '➕ Tab thiếu cột mới',
    'Tab này chưa có cột: ' + missing.join(', ') + '.\n\n' +
    'YES  = thêm các cột đó vào cuối tab rồi import (khuyến nghị).\n' +
    'NO   = giữ nguyên cột hiện có, dữ liệu của các cột đó sẽ bị bỏ qua.',
    ui.ButtonSet.YES_NO
  );
  if (resp !== ui.Button.YES) return existing;

  appendColumns_(ws, existing, missing);
  return existing.concat(missing);
}

// Thêm cột mới vào cuối tab đã có: ghi header, nới merge của title row, set width
function appendColumns_(ws, existing, missing) {
  const startCol = existing.length + 1;
  const newNc = existing.length + missing.length;

  if (ws.getMaxColumns() < newNc) ws.insertColumnsAfter(ws.getMaxColumns(), newNc - ws.getMaxColumns());

  // Title row đang merge theo số cột cũ → phá merge rồi merge lại theo số cột mới
  const titleCell = ws.getRange(1, 1);
  const titleValue = titleCell.getValue();
  ws.getRange(1, 1, 1, newNc).breakApart();
  ws.getRange(1, 1, 1, newNc).merge()
    .setValue(titleValue)
    .setBackground('#1F4E79')
    .setFontColor('#FFFFFF')
    .setFontWeight('bold')
    .setFontSize(12)
    .setFontFamily('Arial')
    .setHorizontalAlignment('center')
    .setVerticalAlignment('middle');

  ws.getRange(2, startCol, 1, missing.length)
    .setValues([missing])
    .setBackground('#BDD7EE')
    .setFontWeight('bold')
    .setFontSize(11)
    .setFontFamily('Arial')
    .setHorizontalAlignment('center')
    .setVerticalAlignment('middle')
    .setWrap(true)
    .setBorder(true, true, true, true, true, true, '#D9D9D9', SpreadsheetApp.BorderStyle.SOLID);

  missing.forEach(function(h, i) {
    ws.setColumnWidth(startCol + i, COLUMN_WIDTHS[h] || 150);
  });
}

// ── TITLE ROW + HEADER ROW ────────────────────────────────────
function writeHeaderRows_(ws, featureTitle) {
  const nc = HEADERS.length;

  // Row 1: Title
  ws.getRange(1, 1, 1, nc).merge()
    .setValue(featureTitle + ' — Test Cases')
    .setBackground('#1F4E79')
    .setFontColor('#FFFFFF')
    .setFontWeight('bold')
    .setFontSize(12)
    .setFontFamily('Arial')
    .setHorizontalAlignment('center')
    .setVerticalAlignment('middle');
  ws.setRowHeight(1, 30);

  // Row 2: Headers
  ws.getRange(2, 1, 1, nc)
    .setValues([HEADERS])
    .setBackground('#BDD7EE')
    .setFontWeight('bold')
    .setFontSize(11)
    .setFontFamily('Arial')
    .setHorizontalAlignment('center')
    .setVerticalAlignment('middle')
    .setWrap(true)
    .setBorder(true, true, true, true, true, true, '#D9D9D9', SpreadsheetApp.BorderStyle.SOLID);
  ws.setRowHeight(2, 26);

  ws.setFrozenRows(2);

  HEADERS.forEach(function(h, i) { ws.setColumnWidth(i + 1, COLUMN_WIDTHS[h] || 150); });
}

// ── DATA ROWS ─────────────────────────────────────────────────
function writeDataRows_(ws, testCases, startRow, headers) {
  headers = headers || HEADERS;
  const nc = headers.length;
  const statusCol = headers.indexOf('Status') + 1;
  const priorityCol = headers.indexOf('Priority') + 1;
  const execCol = headers.indexOf('Execution Type') + 1;

  testCases.forEach(function(tc, i) {
    const row = startRow + i;
    const altBg = row % 2 === 1 ? '#DEEAF1' : '#FFFFFF';

    ws.setRowHeight(row, 90);
    ws.getRange(row, 1, 1, nc)
      .setValues([headers.map(function(h) { return tc[h] || ''; })])
      .setFontFamily('Arial')
      .setFontSize(10)
      .setVerticalAlignment('top')
      .setWrap(true)
      .setBackground(altBg)
      .setBorder(true, true, true, true, true, true, '#D9D9D9', SpreadsheetApp.BorderStyle.SOLID);

    // Status màu
    if (statusCol) {
      ws.getRange(row, statusCol)
        .setBackground(STATUS_COLORS[tc['Status'] || 'Pending'] || '#F2F2F2');
    }

    // Priority màu cam
    if (priorityCol) ws.getRange(row, priorityCol).setBackground('#FCE4D6');

    // Execution Type màu theo giá trị
    if (execCol) {
      ws.getRange(row, execCol)
        .setBackground(EXECUTION_TYPE_COLORS[tc['Execution Type']] || '#FFFFFF');
    }
  });

  const n = testCases.length;

  // Dropdown Status
  if (statusCol) {
    ws.getRange(startRow, statusCol, n, 1).setDataValidation(
      SpreadsheetApp.newDataValidation()
        .requireValueInList(STATUS_VALUES, true)
        .setAllowInvalid(false).build()
    );
  }

  // Dropdown Priority
  if (priorityCol) {
    ws.getRange(startRow, priorityCol, n, 1).setDataValidation(
      SpreadsheetApp.newDataValidation()
        .requireValueInList(['Critical', 'High', 'Medium', 'Low'], true)
        .setAllowInvalid(false).build()
    );
  }

  // Dropdown Execution Type
  if (execCol) {
    ws.getRange(startRow, execCol, n, 1).setDataValidation(
      SpreadsheetApp.newDataValidation()
        .requireValueInList(EXECUTION_TYPE_VALUES, true)
        .setAllowInvalid(false).build()
    );
  }

  // Conditional formatting Status + Execution Type
  const rules = ws.getConditionalFormatRules();
  if (statusCol) {
    const statusRange = ws.getRange(startRow, statusCol, n, 1);
    Object.keys(STATUS_COLORS).forEach(function(status) {
      rules.push(
        SpreadsheetApp.newConditionalFormatRule()
          .whenTextEqualTo(status)
          .setBackground(STATUS_COLORS[status])
          .setRanges([statusRange])
          .build()
      );
    });
  }
  if (execCol) {
    const execRange = ws.getRange(startRow, execCol, n, 1);
    Object.keys(EXECUTION_TYPE_COLORS).forEach(function(v) {
      rules.push(
        SpreadsheetApp.newConditionalFormatRule()
          .whenTextEqualTo(v)
          .setBackground(EXECUTION_TYPE_COLORS[v])
          .setRanges([execRange])
          .build()
      );
    });
  }
  ws.setConditionalFormatRules(rules);
}

// ── MENU ──────────────────────────────────────────────────────
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🧪 Qikify QA')
    .addItem('📋 Import Test Cases từ Claude', 'pushTestCases')
    .addItem('📥 Mở sheet Import', 'openImportSheet')
    .addToUi();
}

function openImportSheet() {
  const ws = ensureImportSheet_();
  SpreadsheetApp.getActiveSpreadsheet().setActiveSheet(ws);
  ws.getRange('B1').activate();
}