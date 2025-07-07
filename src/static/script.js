// Estado da aplicação
let currentUser = null;
let allBooks = [];
let currentFilter = 'todos';

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Carregar livros
    loadBooks();
    
    // Configurar formulário de login
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    
    // Verificar se há usuário logado
    checkAuthStatus();
});

// Navegação entre seções
function showSection(sectionId) {
    // Esconder todas as seções
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Mostrar seção selecionada
    document.getElementById(sectionId).classList.add('active');
    
    // Carregar dados específicos da seção
    switch(sectionId) {
        case 'ranking':
            loadRanking();
            break;
        case 'dashboard':
            if (currentUser) {
                loadUserDashboard();
            } else {
                showSection('login');
            }
            break;
    }
}

// Carregar livros da API
async function loadBooks() {
    try {
        showLoading('livros-container');
        
        const response = await fetch('/api/livros');
        const data = await response.json();
        
        if (data.sucesso) {
            allBooks = data.livros;
            displayBooks(allBooks);
        } else {
            showError('livros-container', 'Erro ao carregar livros');
        }
    } catch (error) {
        console.error('Erro ao carregar livros:', error);
        showError('livros-container', 'Erro de conexão');
    }
}

// Exibir livros na interface
function displayBooks(books) {
    const container = document.getElementById('livros-container');
    
    if (books.length === 0) {
        container.innerHTML = '<p class="loading">Nenhum livro encontrado.</p>';
        return;
    }
    
    container.innerHTML = books.map(book => `
        <div class="livro-card">
            <h3>${book.titulo}</h3>
            <p class="autor">por ${book.autor}</p>
            <span class="genero">${book.genero}</span>
            ${book.obra_regional ? '<span class="regional">Obra Regional</span>' : ''}
            <p>${book.descricao || 'Descrição não disponível'}</p>
        </div>
    `).join('');
}

// Filtrar livros
function filtrarLivros(filtro) {
    currentFilter = filtro;
    
    // Atualizar botões ativos
    document.querySelectorAll('.filters button').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    let filteredBooks = allBooks;
    
    switch(filtro) {
        case 'regionais':
            filteredBooks = allBooks.filter(book => book.obra_regional);
            break;
        case 'romance':
            filteredBooks = allBooks.filter(book => book.genero.toLowerCase().includes('romance'));
            break;
        case 'poesia':
            filteredBooks = allBooks.filter(book => book.genero.toLowerCase().includes('poesia'));
            break;
        default:
            filteredBooks = allBooks;
    }
    
    displayBooks(filteredBooks);
}

// Carregar ranking
async function loadRanking() {
    try {
        showLoading('ranking-container');
        
        const response = await fetch('/api/gamificacao/ranking');
        const data = await response.json();
        
        if (data.sucesso) {
            displayRanking(data.ranking);
        } else {
            showError('ranking-container', 'Erro ao carregar ranking');
        }
    } catch (error) {
        console.error('Erro ao carregar ranking:', error);
        showError('ranking-container', 'Erro de conexão');
    }
}

// Exibir ranking
function displayRanking(ranking) {
    const container = document.getElementById('ranking-container');
    
    if (ranking.length === 0) {
        container.innerHTML = '<p class="loading">Nenhum dado de ranking disponível.</p>';
        return;
    }
    
    container.innerHTML = ranking.map(item => `
        <div class="ranking-item">
            <div class="posicao">${item.posicao}º</div>
            <div class="nome">${item.nome}</div>
            <div class="pontuacao">${item.pontuacao} pts</div>
        </div>
    `).join('');
}

// Lidar com login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const senha = document.getElementById('senha').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ email, senha })
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            currentUser = data.usuario;
            showSuccess('Login realizado com sucesso!');
            updateNavigation();
            showSection('dashboard');
        } else {
            showError('login-form', data.erro || 'Erro no login');
        }
    } catch (error) {
        console.error('Erro no login:', error);
        showError('login-form', 'Erro de conexão');
    }
}

// Verificar status de autenticação
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/me', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.sucesso) {
                currentUser = data.usuario;
                updateNavigation();
            }
        }
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
    }
}

// Atualizar navegação baseada no login
function updateNavigation() {
    const nav = document.querySelector('nav ul');
    
    if (currentUser) {
        // Adicionar opções para usuário logado
        if (!document.querySelector('nav a[onclick="showSection(\'dashboard\')"]')) {
            nav.innerHTML += '<li><a href="#" onclick="showSection(\'dashboard\')">Dashboard</a></li>';
            nav.innerHTML += '<li><a href="#" onclick="logout()">Sair</a></li>';
        }
    }
}

// Carregar dashboard do usuário
async function loadUserDashboard() {
    if (!currentUser) return;
    
    // Exibir informações do usuário
    document.getElementById('user-info').innerHTML = `
        <h3>Bem-vindo, ${currentUser.nome}!</h3>
        <p>Tipo: ${currentUser.tipo_usuario}</p>
        <p>Email: ${currentUser.email}</p>
    `;
    
    // Carregar estatísticas se for aluno
    if (currentUser.tipo_usuario === 'aluno') {
        await loadUserStats();
        await loadUserReadings();
    }
}

// Carregar estatísticas do usuário
async function loadUserStats() {
    try {
        const response = await fetch('/api/leituras/estatisticas', {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            const stats = data.estatisticas;
            document.getElementById('user-stats').innerHTML = `
                <div class="stat-card">
                    <div class="number">${stats.total_leituras}</div>
                    <div class="label">Leituras Iniciadas</div>
                </div>
                <div class="stat-card">
                    <div class="number">${stats.leituras_completas}</div>
                    <div class="label">Leituras Completas</div>
                </div>
                <div class="stat-card">
                    <div class="number">${stats.pontuacao_total}</div>
                    <div class="label">Pontos Totais</div>
                </div>
                <div class="stat-card">
                    <div class="number">${stats.progresso_medio}%</div>
                    <div class="label">Progresso Médio</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// Carregar leituras do usuário
async function loadUserReadings() {
    try {
        const response = await fetch('/api/leituras', {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            displayUserReadings(data.leituras);
        }
    } catch (error) {
        console.error('Erro ao carregar leituras:', error);
    }
}

// Exibir leituras do usuário
function displayUserReadings(readings) {
    const container = document.getElementById('user-readings');
    
    if (readings.length === 0) {
        container.innerHTML = '<h3>Minhas Leituras</h3><p>Você ainda não iniciou nenhuma leitura.</p>';
        return;
    }
    
    container.innerHTML = `
        <h3>Minhas Leituras</h3>
        <div class="livros-grid">
            ${readings.map(reading => `
                <div class="livro-card">
                    <h4>${reading.livro ? reading.livro.titulo : 'Livro não encontrado'}</h4>
                    <p class="autor">${reading.livro ? reading.livro.autor : ''}</p>
                    <div class="progress-bar">
                        <div class="progress" style="width: ${reading.progresso}%"></div>
                    </div>
                    <p>Progresso: ${reading.progresso}%</p>
                    <p>Pontos: ${reading.pontuacao}</p>
                </div>
            `).join('')}
        </div>
    `;
}

// Logout
async function logout() {
    try {
        await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        currentUser = null;
        location.reload(); // Recarregar página para limpar estado
    } catch (error) {
        console.error('Erro no logout:', error);
    }
}

// Funções utilitárias
function showLoading(containerId) {
    document.getElementById(containerId).innerHTML = '<p class="loading">Carregando...</p>';
}

function showError(containerId, message) {
    document.getElementById(containerId).innerHTML = `<p class="error">${message}</p>`;
}

function showSuccess(message) {
    // Criar elemento de sucesso temporário
    const successDiv = document.createElement('div');
    successDiv.className = 'success';
    successDiv.textContent = message;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        document.body.removeChild(successDiv);
    }, 3000);
}

