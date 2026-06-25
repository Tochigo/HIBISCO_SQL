const editor = CodeMirror.fromTextArea(document.getElementById('sql-editor'), {
      mode: 'text/x-sql',
      lineNumbers: true,
      theme: 'material-darker',
      indentWithTabs: false,
      tabSize: 2,
      smartIndent: true,
    });

    let currentSchema = null;
    let currentTable = null;
    let treePreviews = {};
    let currentTreeHtml = '';
    let currentTreeText = '';
    let treeLabelMode = localStorage.getItem('hibiscoTreeLabelMode') || 'symbols';

    const executeQueryBtn = document.getElementById('executeQueryBtn');
    const clearBtn = document.getElementById('clearBtn');
    const statusMessage = document.getElementById('statusMessage');
    const descriptionOutput = document.getElementById('descriptionOutput');
    const treeOutput = document.getElementById('treeOutput');
    const treePreviewTooltip = document.getElementById('treePreviewTooltip');
    const treeLabelToggle = document.getElementById('treeLabelToggle');
    const treeLabelModeText = document.getElementById('treeLabelModeText');
    const emptyResults = document.getElementById('emptyResults');
    const resultsTableContainer = document.getElementById('resultsTableContainer');
    const resultsHead = document.getElementById('resultsHead');
    const resultsBody = document.getElementById('resultsBody');

    const schemaTabs = document.getElementById('schemaTabs');
    const tableList = document.getElementById('tableList');
    const tableStatus = document.getElementById('tableStatus');
    const emptyPreview = document.getElementById('emptyPreview');
    const previewTableContainer = document.getElementById('previewTableContainer');
    const previewHead = document.getElementById('previewHead');
    const previewBody = document.getElementById('previewBody');

    function formatRelationalLabel(label) {
      if (treeLabelMode !== 'words') {
        return label;
      }

      let formatted = String(label || '');

      const exactLabels = {
        'π': 'proyección',
        'σ': 'selección',
        'ρ': 'renombre',
        '⨝': 'join',
        '∪': 'unión',
        '∩': 'intersección',
        '−': 'diferencia',
        'distinct': 'sin duplicados',
        'with': 'with',
        'subquery': 'subconsulta',
        'UNKNOWN_SOURCE': 'fuente desconocida',
      };

      if (exactLabels[formatted]) {
        return exactLabels[formatted];
      }

      const prefixLabels = [
        ['π[', 'proyección['],
        ['σ[', 'selección['],
        ['ρ[', 'renombre['],
        ['⨝[', 'join['],
        ['group by[', 'agrupación['],
        ['aggregation[', 'agregación['],
        ['having[', 'filtro having['],
        ['order by[', 'ordenamiento['],
        ['limit[', 'límite['],
        ['offset[', 'desplazamiento['],
        ['cte[', 'cte['],
      ];

      prefixLabels.forEach(([symbolPrefix, wordPrefix]) => {
        if (formatted.startsWith(symbolPrefix)) {
          formatted = wordPrefix + formatted.slice(symbolPrefix.length);
        }
      });

      return formatted.replaceAll('aggregation[', 'agregación[');
    }

    function applyTreeLabelModeToHtml(treeHtml) {
      if (!treeHtml || treeLabelMode !== 'words') {
        return treeHtml;
      }

      const wrapper = document.createElement('div');
      wrapper.innerHTML = treeHtml;

      wrapper.querySelectorAll('.tree-node').forEach((node) => {
        node.textContent = formatRelationalLabel(node.textContent);
      });

      return wrapper.innerHTML;
    }

    function formatPlainTreeText(treeText) {
      if (!treeText || treeLabelMode !== 'words') {
        return treeText;
      }

      return treeText
        .split('\n')
        .map((line) => line.replace(/^(.*[├└]──\s*)(.*)$/u, (_match, prefix, label) => {
          return `${prefix}${formatRelationalLabel(label)}`;
        }))
        .join('\n');
    }

    function updateTreeToggleUi() {
      if (!treeLabelToggle) return;

      treeLabelToggle.checked = treeLabelMode === 'words';

      if (treeLabelModeText) {
        treeLabelModeText.textContent = treeLabelMode === 'words' ? 'Palabras' : 'Palabras';
      }
    }

    function renderTreeOutput() {
      hideTreePreview();

      if (currentTreeHtml) {
        treeOutput.innerHTML = applyTreeLabelModeToHtml(currentTreeHtml);
        bindTreeNodeEvents();
        return;
      }

      if (currentTreeText) {
        treeOutput.textContent = formatPlainTreeText(currentTreeText);
        return;
      }

      treeOutput.textContent = 'El árbol relacional aparecerá aquí después de ejecutar una consulta.';
    }

    function setStatus(message, type = '') {
      statusMessage.textContent = message;
      statusMessage.className = 'status-message';
      if (type) statusMessage.classList.add(type);
      statusMessage.classList.remove('hidden');
    }

    function clearOutputs() {
      descriptionOutput.textContent = 'Los pasos de ejecución aparecerán aquí después de ejecutar una consulta.';
      currentTreeHtml = '';
      currentTreeText = '';
      treeOutput.textContent = 'El árbol relacional aparecerá aquí después de ejecutar una consulta.';
      treePreviews = {};
      hideTreePreview();
      resultsHead.innerHTML = '';
      resultsBody.innerHTML = '';
      emptyResults.textContent = 'No hay resultados para mostrar. Ejecuta una consulta para ver los datos.';
      emptyResults.classList.remove('hidden');
      resultsTableContainer.classList.add('hidden');
      statusMessage.classList.add('hidden');
    }

    function escapeHtml(value) {
      return String(value ?? 'NULL')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
    }

    function renderTable(columns, rows, headElement, bodyElement, containerElement, emptyElement, emptyMessage = 'No hay datos para mostrar.') {
      headElement.innerHTML = '';
      bodyElement.innerHTML = '';

      if (!columns || columns.length === 0) {
        emptyElement.textContent = 'La consulta no devolvió columnas.';
        emptyElement.classList.remove('hidden');
        containerElement.classList.add('hidden');
        return;
      }

      const headerRow = document.createElement('tr');
      columns.forEach((col) => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
      });
      headElement.appendChild(headerRow);

      if (!rows || rows.length === 0) {
        emptyElement.textContent = emptyMessage;
        emptyElement.classList.remove('hidden');
        containerElement.classList.add('hidden');
        return;
      }

      rows.forEach((row) => {
        const tr = document.createElement('tr');

        row.forEach((cell) => {
          const td = document.createElement('td');
          td.innerHTML = escapeHtml(cell);
          tr.appendChild(td);
        });

        bodyElement.appendChild(tr);
      });

      emptyElement.classList.add('hidden');
      containerElement.classList.remove('hidden');
    }


    function renderPreviewTooltip(preview) {
      if (!preview) {
        return '<div class="tree-preview-message">No hay vista previa disponible para este nodo.</div>';
      }

      if (preview.error) {
        return `
          <div class="tree-preview-title">${escapeHtml(formatRelationalLabel(preview.label || 'Nodo del árbol'))}</div>
          <div class="tree-preview-error">${escapeHtml(preview.error)}</div>
        `;
      }

      const columns = preview.columns || [];
      const rows = preview.rows || [];

      const sqlBlock = preview.sql
        ? `<div class="tree-preview-sql">${escapeHtml(preview.sql)}</div>`
        : '';

      if (columns.length === 0) {
        return `
          <div class="tree-preview-title">${escapeHtml(formatRelationalLabel(preview.label || 'Nodo del árbol'))}</div>
          ${sqlBlock}
          <div class="tree-preview-message">Este nodo no tiene columnas para mostrar.</div>
        `;
      }

      const headHtml = columns
        .map((col) => `<th>${escapeHtml(col)}</th>`)
        .join('');

      const bodyHtml = rows.length > 0
        ? rows.map((row) => `
            <tr>
              ${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join('')}
            </tr>
          `).join('')
        : `<tr><td colspan="${columns.length}">No hay filas para mostrar.</td></tr>`;

      const compactClass = columns.length >= 7 ? ' compact' : '';
      const veryCompactClass = columns.length >= 10 ? ' very-compact' : '';

      return `
        <div class="tree-preview-title">${escapeHtml(formatRelationalLabel(preview.label || 'Nodo del árbol'))}</div>
        ${sqlBlock}
        <table class="tree-preview-table${compactClass}${veryCompactClass}">
          <thead>
            <tr>${headHtml}</tr>
          </thead>
          <tbody>${bodyHtml}</tbody>
        </table>
      `;
    }

    function positionTreePreview(nodeElement) {
      const offset = 12;

      const nodeRect = nodeElement.getBoundingClientRect();

      treePreviewTooltip.style.left = '0px';
      treePreviewTooltip.style.top = '0px';

      const tooltipRect = treePreviewTooltip.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      let left = nodeRect.left;
      let top = nodeRect.bottom + offset;

      const fitsBelow = top + tooltipRect.height <= viewportHeight - offset;

      if (!fitsBelow) {
        top = nodeRect.top - tooltipRect.height - offset;
      }

      if (left + tooltipRect.width > viewportWidth - offset) {
        left = viewportWidth - tooltipRect.width - offset;
      }

      left = Math.max(offset, left);
      top = Math.max(offset, top);

      treePreviewTooltip.style.left = `${left}px`;
      treePreviewTooltip.style.top = `${top}px`;
    }

    function showTreePreview(nodeElement) {
      const nodeId = nodeElement.dataset.nodeId;
      const preview = treePreviews[nodeId];

      treePreviewTooltip.innerHTML = renderPreviewTooltip(preview);
      treePreviewTooltip.style.display = 'block';

      positionTreePreview(nodeElement);
    }
    
    function hideTreePreview() {
      if (!treePreviewTooltip) return;
      treePreviewTooltip.style.display = 'none';
    }

    function bindTreeNodeEvents() {
      document.querySelectorAll('.tree-node').forEach((node) => {
        node.addEventListener('mouseenter', () => {
          showTreePreview(node);
        });

        node.addEventListener('mouseleave', hideTreePreview);
      });
    }

    function getActiveSchema() {
      const activeSchemaBtn = document.querySelector('[data-schema].active');

      if (currentSchema) {
        return currentSchema;
      }

      if (activeSchemaBtn) {
        return activeSchemaBtn.dataset.schema;
      }

      return '';
    }

    async function runQuery(sql) {
      const activeSchema = getActiveSchema();

      const response = await fetch('/sql/run/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: sql,
          schema: activeSchema,
        }),
      });

      return response.json();
    }

    async function fetchJson(url) {
      const response = await fetch(url);
      return response.json();
    }

    async function postJson(url, payload) {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      return response.json();
    }

    function clearPreview(message = 'Selecciona una tabla para ver sus datos.') {
      previewHead.innerHTML = '';
      previewBody.innerHTML = '';
      previewTableContainer.classList.add('hidden');
      emptyPreview.textContent = message;
      emptyPreview.classList.remove('hidden');
    }

    async function loadSchemas() {
      tableStatus.textContent = 'Cargando esquemas...';
      schemaTabs.innerHTML = '';
      tableList.innerHTML = '<div class="empty-results">Cargando esquemas...</div>';
      clearPreview('Selecciona un esquema y una tabla para ver sus datos.');

      try {
        const data = await fetchJson('/sql/schemas/');

        if (!data.ok) {
          tableStatus.textContent = 'No se pudieron cargar los esquemas.';
          tableList.innerHTML = `<div class="empty-results">${escapeHtml(data.error || 'Error desconocido.')}</div>`;
          return;
        }

        const schemas = data.schemas || [];

        if (schemas.length === 0) {
          tableStatus.textContent = 'No hay esquemas disponibles.';
          tableList.innerHTML = '<div class="empty-results">No hay esquemas para mostrar.</div>';
          return;
        }

        schemas.forEach((schemaName, index) => {
          const btn = document.createElement('button');
          btn.className = `tab-btn${index === 0 ? ' active' : ''}`;
          btn.type = 'button';
          btn.textContent = schemaName;
          btn.dataset.schema = schemaName;
          btn.addEventListener('click', () => selectSchema(schemaName, btn));
          schemaTabs.appendChild(btn);
        });

        await selectSchema(schemas[0], schemaTabs.querySelector('[data-schema]'));
      } catch (error) {
        tableStatus.textContent = 'No se pudo conectar con el backend para cargar los esquemas.';
        tableList.innerHTML = `<div class="empty-results">${escapeHtml(error)}</div>`;
      }
    }

    async function selectSchema(schemaName, buttonElement) {
      currentSchema = schemaName;
      currentTable = null;

      document.querySelectorAll('[data-schema]').forEach((btn) => btn.classList.remove('active'));
      if (buttonElement) buttonElement.classList.add('active');

      tableStatus.textContent = `Cargando tablas del esquema ${schemaName}...`;
      tableList.innerHTML = '<div class="empty-results">Cargando tablas...</div>';
      clearPreview('Selecciona una tabla para ver sus datos.');

      try {
        const data = await fetchJson(`/sql/tables/?schema=${encodeURIComponent(schemaName)}`);

        if (!data.ok) {
          tableStatus.textContent = `No se pudieron cargar las tablas de ${schemaName}.`;
          tableList.innerHTML = `<div class="empty-results">${escapeHtml(data.error || 'Error desconocido.')}</div>`;
          return;
        }

        renderTableList(data.tables || []);
        tableStatus.textContent = `Esquema activo: ${schemaName}. Tablas disponibles: ${(data.tables || []).length}.`;
      } catch (error) {
        tableStatus.textContent = `No se pudo conectar con el backend para cargar las tablas de ${schemaName}.`;
        tableList.innerHTML = `<div class="empty-results">${escapeHtml(error)}</div>`;
      }
    }

    function renderTableList(tables) {
      tableList.innerHTML = '';

      if (tables.length === 0) {
        tableList.innerHTML = '<div class="empty-results">Este esquema no tiene tablas.</div>';
        return;
      }

      tables.forEach((tableName, index) => {
        const btn = document.createElement('button');
        btn.className = `table-list-btn${index === 0 ? ' active' : ''}`;
        btn.type = 'button';
        btn.textContent = tableName;
        btn.dataset.table = tableName;
        btn.addEventListener('click', () => selectTable(tableName, btn));
        tableList.appendChild(btn);
      });

      const firstButton = tableList.querySelector('[data-table]');
      if (firstButton) {
        selectTable(firstButton.dataset.table, firstButton);
      }
    }

    async function selectTable(tableName, buttonElement) {
      if (!currentSchema) return;

      currentTable = tableName;

      document.querySelectorAll('[data-table]').forEach((btn) => btn.classList.remove('active'));
      if (buttonElement) buttonElement.classList.add('active');

      await loadTablePreview(currentSchema, tableName);
    }
    
    async function loadTablePreview(schemaName, tableName) {
      tableStatus.textContent = `Cargando ${schemaName}.${tableName}...`;
      previewHead.innerHTML = '';
      previewBody.innerHTML = '';
      emptyPreview.classList.add('hidden');
      previewTableContainer.classList.remove('hidden');

      try {
        const data = await postJson('/sql/preview-table/', {
          schema: schemaName,
          table: tableName,
        });

        if (!data.ok) {
          tableStatus.textContent = `No se pudo cargar ${schemaName}.${tableName}.`;
          emptyPreview.textContent = data.error || 'Error desconocido al cargar la tabla.';
          emptyPreview.classList.remove('hidden');
          previewTableContainer.classList.add('hidden');
          return;
        }

        renderTable(
          data.columns || [],
          data.rows || [],
          previewHead,
          previewBody,
          previewTableContainer,
          emptyPreview,
          `La tabla ${schemaName}.${tableName} no tiene registros.`
        );

        tableStatus.textContent = `Tabla activa: ${schemaName}.${tableName}. Filas mostradas: ${(data.rows || []).length}.`;
      } catch (error) {
        tableStatus.textContent = `No se pudo conectar con el backend para cargar ${schemaName}.${tableName}.`;
        emptyPreview.textContent = String(error);
        emptyPreview.classList.remove('hidden');
        previewTableContainer.classList.add('hidden');
      }
    }

    executeQueryBtn.addEventListener('click', async () => {
      const sql = editor.getValue().trim();

      const activeSchema = getActiveSchema();

      if (!activeSchema) {
        setStatus('Error con el esquema seleccionado.', 'error');
        return;
      }

      if (!sql) {
        setStatus('No has escrito ninguna consulta SQL.', 'error');
        return;
      }

      executeQueryBtn.disabled = true;
      setStatus('Ejecutando consulta...', '');
      descriptionOutput.textContent = '';
      currentTreeHtml = '';
      currentTreeText = '';
      treeOutput.textContent = '';
      treePreviews = {};
      hideTreePreview();
      resultsHead.innerHTML = '';
      resultsBody.innerHTML = '';
      emptyResults.classList.add('hidden');
      resultsTableContainer.classList.add('hidden');

      try {
        const data = await runQuery(sql);

        if (!data.ok) {
          const errorMessage = data.error || 'No se recibió detalle del error.';

          setStatus(`Error en sintaxis de la consulta.\n${errorMessage}`, 'error');

          descriptionOutput.textContent = '';
          currentTreeHtml = '';
          currentTreeText = '';
          treeOutput.textContent = '';
          treePreviews = {};
          hideTreePreview();

          emptyResults.textContent = 'La consulta falló. Revisa el mensaje de error mostrado arriba.';
          emptyResults.classList.remove('hidden');
          resultsTableContainer.classList.add('hidden');

          return;
        }

        renderTable(
          data.columns || [],
          data.rows || [],
          resultsHead,
          resultsBody,
          resultsTableContainer,
          emptyResults,
          'La consulta se ejecutó correctamente, pero no devolvió filas.'
        );

        if (Array.isArray(data.description) && data.description.length > 0) {
          descriptionOutput.textContent = data.description.join('\n');
        } else if (typeof data.description === 'string' && data.description.trim()) {
          descriptionOutput.textContent = data.description;
        } else {
          descriptionOutput.textContent = 'No se generó descripción.';
        }

        treePreviews = data.tree_previews || {};
        currentTreeHtml = data.tree_html || '';
        currentTreeText = data.tree || '';

        if (currentTreeHtml || currentTreeText) {
          renderTreeOutput();
        } else {
          treeOutput.textContent = 'No se generó árbol relacional.';
        }

        setStatus(`Consulta ejecutada correctamente. Filas obtenidas: ${(data.rows || []).length}.`, 'success');
        } catch (error) {
          setStatus(`Error al conectar con el backend.\n${String(error)}`, 'error');

          descriptionOutput.textContent = '';
          currentTreeHtml = '';
          currentTreeText = '';
          treeOutput.textContent = '';
          treePreviews = {};
          hideTreePreview();

          emptyResults.textContent = 'No se pudo conectar con el backend.';
          emptyResults.classList.remove('hidden');
          resultsTableContainer.classList.add('hidden');
        } finally {
        executeQueryBtn.disabled = false;
      }
    });

    if (treeLabelToggle) {
      updateTreeToggleUi();

      treeLabelToggle.addEventListener('change', () => {
        treeLabelMode = treeLabelToggle.checked ? 'words' : 'symbols';
        localStorage.setItem('hibiscoTreeLabelMode', treeLabelMode);
        updateTreeToggleUi();
        renderTreeOutput();
      });
    }

    clearBtn.addEventListener('click', clearOutputs);
    function syncEditorTheme(isDark) {
      editor.setOption('theme', isDark ? 'material-darker' : 'eclipse');
    }

    document.addEventListener('hibisco:theme-change', function (event) {
      syncEditorTheme(event.detail.isDark);
    });

    syncEditorTheme(document.body.classList.contains('dark'));
    loadSchemas();
