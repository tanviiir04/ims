document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();
            if (response.ok) {
                window.location.href = 'index.html';
            } else {
                document.getElementById('error').textContent = data.message || 'Login failed';
            }
        });
    }

    const assignedFilter = document.getElementById('assignedFilter');
    const priorityFilter = document.getElementById('priorityFilter');
    const resolvedFilter = document.getElementById('resolvedFilter');
    const incidentsContainer = document.getElementById('incidents');
    const createIncidentForm = document.getElementById('createIncidentForm');
    const incidentTitle = document.getElementById('incidentTitle');
    const incidentDescription = document.getElementById('incidentDescription');
    const incidentPriority = document.getElementById('incidentPriority');
    const incidentCategory = document.getElementById('incidentCategory');
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    const refreshBtn = document.getElementById('refreshBtn');
    const exportBtn = document.getElementById('exportBtn');
    const ticketDetails = document.getElementById('ticketDetails');
    const ticketBody = ticketDetails?.querySelector('.card-body');

    let allUsers = [];
    let allIncidents = [];

    async function loadUsers() {
        const response = await fetch('/api/users', { credentials: 'include' });
        if (!response.ok) return;
        allUsers = await response.json();
        if (assignedFilter) {
            assignedFilter.innerHTML = `
                <option value="all">All Assignees</option>
                <option value="unassigned">Not Assigned</option>
            `;
            allUsers.forEach(u => {
                const opt = document.createElement('option');
                opt.value = u.id;
                opt.textContent = u.name;
                assignedFilter.appendChild(opt);
            });
        }
    }

    async function loadIncidents() {
        const response = await fetch('/api/incidents', { credentials: 'include' });
        if (!response.ok) return;
        allIncidents = await response.json();
        renderIncidents(allIncidents);
    }

    function renderIncidents(incidents) {
        if (!incidentsContainer) return;
        incidentsContainer.innerHTML = '';

        if (incidents.length === 0) {
            const emptyMsg = document.createElement('div');
            emptyMsg.className = 'text-muted text-center p-3';
            emptyMsg.textContent = '🔍 No incidents found';
            incidentsContainer.appendChild(emptyMsg);
            return;
        }

        incidents.forEach(incident => {
            const assignedUser = allUsers.find(u => u.id === incident.assigned_to);
            const assignedName = assignedUser ? assignedUser.name : 'Not Assigned';
            const statusColor = incident.status === 'resolved' ? 'warning' : 'primary';
            const priorityColor = {
                critical: 'danger',
                high: 'danger',
                medium: 'warning',
                low: 'info'
            }[incident.priority] || 'secondary';

            const item = document.createElement('div');
            item.className = 'list-group-item d-flex justify-content-between align-items-center incident-item';
            item.setAttribute('data-id', incident.id);
            item.innerHTML = `
                <div><span class="text-muted">#${incident.id}</span> <strong class="ms-2">${incident.title}</strong></div>
                <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-${statusColor}">${incident.status}</span>
                    <span class="badge bg-${priorityColor}">${incident.priority}</span>
                    <span>${assignedName}</span>
                </div>
            `;
            item.addEventListener('click', () => showIncidentDetails(incident));
            incidentsContainer.appendChild(item);
        });
    }

    function showIncidentDetails(incident) {
        ticketDetails.style.display = 'block';
        ticketBody.innerHTML = `
            <p><strong>Title:</strong> ${incident.title}</p>
            <p><strong>Description:</strong> ${incident.description || 'No description'}</p>
            <p><strong>Status:</strong> ${incident.status}</p>
            <p><strong>Priority:</strong> ${incident.priority}</p>
            <p><strong>Category:</strong> ${incident.category}</p>
            <p><strong>Assigned to:</strong> ${
                allUsers.find(u => u.id === incident.assigned_to)?.name || 'Not Assigned'
            }</p>
            <p><strong>Created at:</strong> ${new Date(incident.createdAt).toLocaleString()}</p>
        `;
    }

    if (createIncidentForm) {
        createIncidentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = incidentTitle.value;
            const description = incidentDescription.value;
            const priority = incidentPriority.value;
            const category = incidentCategory.value;
            const assignedToValue = assignedFilter?.value;
            const response = await fetch('/api/incidents', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    title,
                    description,
                    priority,
                    category,
                    assigned_to: assignedToValue !== 'all' ? assignedToValue : null
                })
            });
            if (response.ok) {
                loadIncidents();
                createIncidentForm.reset();
            } else {
                alert('Failed to create incident');
            }
        });
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim().toLowerCase();
            const filtered = allIncidents.filter(i =>
                i.title.toLowerCase().includes(query) ||
                i.description.toLowerCase().includes(query)
            );
            renderIncidents(filtered);
        });
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadIncidents();
        });
    }

    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            const csv = ['ID,Title,Status,Priority,Assignee'];
            allIncidents.forEach(i => {
                const assignedName = allUsers.find(u => u.id === i.assigned_to)?.name || 'Not Assigned';
                csv.push(`${i.id},"${i.title}",${i.status},${i.priority},"${assignedName}"`);
            });
            const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'incidents.csv';
            a.click();
        });
    }

    if (assignedFilter && incidentsContainer) {
        loadUsers();
        loadIncidents();
    }
});
