def create_generic_dashboard(db):
    """Crée un dashboard générique pour toutes les équipes"""
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard FTTH - MG TELECOM</title>
    <style>
        :root {
            --primary: #3b82f6;
            --primary-dark: #1d4ed8;
            --secondary: #10b981;
            --accent: #8b5cf6;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #0f172a;
            --light: #f8fafc;
            --gray: #64748b;
            --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --gradient-4: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: var(--light);
            min-height: 100vh;
            line-height: 1.6;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Hero Section */
        .hero {
            text-align: center;
            padding: 60px 20px;
            background: var(--gradient-1);
            border-radius: 25px;
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.1' fill-rule='evenodd'/%3E%3C/svg%3E");
        }
        
        .hero h1 {
            font-size: 48px;
            margin-bottom: 20px;
            position: relative;
            z-index: 2;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        .hero p {
            font-size: 20px;
            max-width: 600px;
            margin: 0 auto 30px;
            position: relative;
            z-index: 2;
            opacity: 0.9;
        }
        
        .hero-badges {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
            position: relative;
            z-index: 2;
        }
        
        .hero-badge {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 10px 20px;
            border-radius: 50px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Quick Stats */
        .quick-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .stat-card:hover {
            transform: translateY(-10px);
            border-color: var(--primary);
            box-shadow: 0 15px 40px rgba(59, 130, 246, 0.2);
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: var(--gradient-2);
        }
        
        .stat-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-icon {
            width: 60px;
            height: 60px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }
        
        .stat-title {
            font-size: 20px;
            font-weight: 600;
            color: var(--light);
        }
        
        .stat-number {
            font-size: 52px;
            font-weight: 800;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            line-height: 1;
        }
        
        .stat-subtitle {
            color: var(--gray);
            font-size: 14px;
        }
        
        /* Teams Grid */
        .teams-section {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 25px;
            padding: 40px;
            margin-bottom: 40px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .section-title {
            font-size: 28px;
            font-weight: 700;
            background: var(--gradient-3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .section-subtitle {
            color: var(--gray);
            font-size: 16px;
        }
        
        .teams-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }
        
        .team-card {
            background: rgba(30, 41, 59, 0.7);
            border-radius: 20px;
            padding: 30px;
            border: 2px solid transparent;
            transition: all 0.4s;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .team-card:hover {
            transform: translateY(-8px) scale(1.02);
            border-color: var(--primary);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        }
        
        .team-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.05), transparent);
            transform: translateX(-100%);
        }
        
        .team-card:hover::before {
            animation: shine 1s;
        }
        
        @keyframes shine {
            100% {
                transform: translateX(100%);
            }
        }
        
        .team-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .team-avatar {
            width: 70px;
            height: 70px;
            background: var(--gradient-4);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: 800;
            color: var(--dark);
            box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
        }
        
        .team-info h3 {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .team-info p {
            color: var(--gray);
            font-size: 14px;
        }
        
        .team-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 25px 0;
        }
        
        .team-stat {
            text-align: center;
        }
        
        .team-stat-number {
            font-size: 32px;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 5px;
        }
        
        .team-stat-label {
            font-size: 12px;
            color: var(--gray);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .team-progress {
            margin-top: 20px;
        }
        
        .progress-bar {
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--gradient-4);
            border-radius: 4px;
            transition: width 1s ease;
        }
        
        /* Fun Elements */
        .fun-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .fun-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
            transition: all 0.3s;
        }
        
        .fun-card:hover {
            transform: translateY(-5px);
            border-color: var(--accent);
        }
        
        .fun-icon {
            font-size: 60px;
            margin-bottom: 20px;
        }
        
        .fun-title {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 15px;
            background: var(--gradient-2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .fun-text {
            color: var(--gray);
            line-height: 1.6;
        }
        
        /* Achievements */
        .achievements {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: center;
            margin: 40px 0;
        }
        
        .achievement-badge {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 50px;
            padding: 12px 25px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .achievement-badge:hover {
            background: rgba(59, 130, 246, 0.2);
            border-color: var(--primary);
            transform: scale(1.05);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 40px 20px;
            margin-top: 60px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .footer-logo {
            font-size: 32px;
            font-weight: 800;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
        
        .footer-text {
            color: var(--gray);
            max-width: 600px;
            margin: 0 auto 30px;
        }
        
        .social-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 30px 0;
        }
        
        .social-link {
            width: 50px;
            height: 50px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: var(--light);
            font-size: 20px;
            transition: all 0.3s;
        }
        
        .social-link:hover {
            background: var(--primary);
            transform: translateY(-5px);
        }
        
        /* Animations */
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .floating {
            animation: float 3s ease-in-out infinite;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 32px;
            }
            
            .teams-grid {
                grid-template-columns: 1fr;
            }
            
            .quick-stats {
                grid-template-columns: 1fr;
            }
            
            .section-header {
                flex-direction: column;
                text-align: center;
                gap: 15px;
            }
        }
        
        /* Particle Background */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }
    </style>
</head>
<body>
    <!-- Particle Background -->
    <div class="particles" id="particles"></div>
    
    <div class="container">
        <!-- Hero Section -->
        <section class="hero">
            <h1>🚀 Dashboard FTTH</h1>
            <p>Bienvenue dans l'interface de gestion des installations fibre optique. Suivez vos performances et progressez avec votre équipe !</p>
            
            <div class="hero-badges">
                <div class="hero-badge">
                    <span>📊</span>
                    <span>Analytique en temps réel</span>
                </div>
                <div class="hero-badge">
                    <span>⚡</span>
                    <span>Performance optimisée</span>
                </div>
                <div class="hero-badge">
                    <span>🔒</span>
                    <span>Données sécurisées</span>
                </div>
            </div>
        </section>
        
        <!-- Quick Stats -->
        <div class="quick-stats">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">📈</div>
                    <div>
                        <div class="stat-title">Installations Total</div>
                        <div class="stat-subtitle">Depuis le début</div>
                    </div>
                </div>
                <div class="stat-number" id="totalInstallations">0</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 85%"></div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">👥</div>
                    <div>
                        <div class="stat-title">Équipes Actives</div>
                        <div class="stat-subtitle">En service aujourd'hui</div>
                    </div>
                </div>
                <div class="stat-number" id="activeTeams">0</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 70%"></div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon">🎯</div>
                    <div>
                        <div class="stat-title">Taux de Réussite</div>
                        <div class="stat-subtitle">Installations réussies</div>
                    </div>
                </div>
                <div class="stat-number" id="successRate">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 92%"></div>
                </div>
            </div>
        </div>
        
        <!-- Teams Section -->
        <section class="teams-section">
            <div class="section-header">
                <div>
                    <h2 class="section-title">🏆 Classement des Équipes</h2>
                    <p class="section-subtitle">Performance basée sur les installations du mois</p>
                </div>
                <div style="color: var(--gray); font-size: 14px;">
                    Mise à jour quotidienne
                </div>
            </div>
            
            <div class="teams-grid" id="teamsGrid">
                <!-- Les équipes seront chargées ici par JavaScript -->
            </div>
        </section>
        
        <!-- Fun Elements -->
        <div class="fun-section">
            <div class="fun-card">
                <div class="fun-icon floating">🏅</div>
                <h3 class="fun-title">Badges de Performance</h3>
                <p class="fun-text">Débloquez des badges en fonction de vos performances. Chaque objectif atteint vous rapproche du niveau supérieur !</p>
                <div class="achievements">
                    <div class="achievement-badge">
                        <span>🥇</span>
                        <span>Équipe du Mois</span>
                    </div>
                    <div class="achievement-badge">
                        <span>⚡</span>
                        <span>Installation Rapide</span>
                    </div>
                </div>
            </div>
            
            <div class="fun-card">
                <div class="fun-icon floating">📱</div>
                <h3 class="fun-title">Interface Mobile</h3>
                <p class="fun-text">Accédez à vos données depuis n'importe où. L'interface s'adapte parfaitement à tous vos appareils mobiles.</p>
                <div class="achievements">
                    <div class="achievement-badge">
                        <span>📲</span>
                        <span>Mobile Optimisé</span>
                    </div>
                    <div class="achievement-badge">
                        <span>🌐</span>
                        <span>Hors Ligne</span>
                    </div>
                </div>
            </div>
            
            <div class="fun-card">
                <div class="fun-icon floating">🎮</div>
                <h3 class="fun-title">Mode Ludique</h3>
                <p class="fun-text">Transformez votre travail en jeu ! Gagnez des points, montez de niveau et défiez les autres équipes.</p>
                <div class="achievements">
                    <div class="achievement-badge">
                        <span>🎯</span>
                        <span>Objectifs Quotidiens</span>
                    </div>
                    <div class="achievement-badge">
                        <span>🏆</span>
                        <span>Leaderboard</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- More Achievements -->
        <div class="achievements">
            <div class="achievement-badge">
                <span>🌟</span>
                <span>Nouveau Record</span>
            </div>
            <div class="achievement-badge">
                <span>🚀</span>
                <span>Performance x2</span>
            </div>
            <div class="achievement-badge">
                <span>💎</span>
                <span>Qualité Premium</span>
            </div>
            <div class="achievement-badge">
                <span>🎪</span>
                <span>Équipe Complète</span>
            </div>
            <div class="achievement-badge">
                <span>🔧</span>
                <span>Expert Technique</span>
            </div>
        </div>
        
        <!-- Footer -->
        <footer class="footer">
            <div class="footer-logo">MG TELECOM FTTH</div>
            <p class="footer-text">
                Système de gestion des installations fibre optique. Suivez vos performances, 
                gérez vos équipes et optimisez vos opérations.
            </p>
            
            <div class="social-links">
                <a href="#" class="social-link">
                    <span>📱</span>
                </a>
                <a href="#" class="social-link">
                    <span>📧</span>
                </a>
                <a href="#" class="social-link">
                    <span>📊</span>
                </a>
                <a href="#" class="social-link">
                    <span>⚙️</span>
                </a>
            </div>
            
            <div style="color: var(--gray); font-size: 14px; margin-top: 30px;">
                <p>💡 Conseil du jour : "Une bonne préparation fait 90% du travail réussi"</p>
                <p style="margin-top: 10px; font-size: 12px;">by Nylockdev • Dernière mise à jour : <span id="currentDate">...</span></p>
            </div>
        </footer>
    </div>
    
    <script>
        // Données de test (seront remplacées par les vraies données)
        const teamsData = [
            { name: "WINAT", installations: 156, clients: 142, level: 8, color: "#3b82f6" },
            { name: "GOLD", installations: 132, clients: 128, level: 7, color: "#f59e0b" },
            { name: "ELITE", installations: 98, clients: 95, level: 6, color: "#10b981" },
            { name: "PRO", installations: 87, clients: 84, level: 5, color: "#8b5cf6" },
            { name: "TECH", installations: 65, clients: 62, level: 4, color: "#ef4444" },
            { name: "SPEED", installations: 45, clients: 43, level: 3, color: "#06b6d4" }
        ];
        
        // Fonction pour formater les nombres
        function formatNumber(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        }
        
        // Initialiser les stats
        function initStats() {
            const totalInstallations = teamsData.reduce((sum, team) => sum + team.installations, 0);
            const totalClients = teamsData.reduce((sum, team) => sum + team.clients, 0);
            const successRate = Math.round((totalClients / totalInstallations) * 100);
            
            document.getElementById('totalInstallations').textContent = formatNumber(totalInstallations);
            document.getElementById('activeTeams').textContent = teamsData.length;
            document.getElementById('successRate').textContent = successRate + '%';
            document.getElementById('currentDate').textContent = new Date().toLocaleDateString('fr-FR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
        
        // Générer les cartes d'équipe
        function generateTeamCards() {
            const teamsGrid = document.getElementById('teamsGrid');
            teamsGrid.innerHTML = '';
            
            // Trier par installations (décroissant)
            const sortedTeams = [...teamsData].sort((a, b) => b.installations - a.installations);
            
            sortedTeams.forEach((team, index) => {
                const rank = index + 1;
                const rankEmoji = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : '🎯';
                const progress = Math.min(100, (team.installations / 200) * 100);
                
                const teamCard = document.createElement('div');
                teamCard.className = 'team-card';
                teamCard.onclick = () => {
                    window.location.href = `dashboard_${team.name}.html`;
                };
                
                teamCard.innerHTML = `
                    <div class="team-header">
                        <div class="team-avatar" style="background: linear-gradient(135deg, ${team.color} 0%, ${team.color}80 100%);">
                            ${team.name.charAt(0)}
                        </div>
                        <div class="team-info">
                            <h3>${rankEmoji} ${team.name}</h3>
                            <p>Niveau ${team.level} • ${team.installations} installations</p>
                        </div>
                    </div>
                    
                    <div class="team-stats">
                        <div class="team-stat">
                            <div class="team-stat-number">${formatNumber(team.installations)}</div>
                            <div class="team-stat-label">Installations</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-number">${formatNumber(team.clients)}</div>
                            <div class="team-stat-label">Clients</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-number">${Math.round((team.clients / team.installations) * 100)}%</div>
                            <div class="team-stat-label">Réussite</div>
                        </div>
                        <div class="team-stat">
                            <div class="team-stat-number">#${rank}</div>
                            <div class="team-stat-label">Classement</div>
                        </div>
                    </div>
                    
                    <div class="team-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--gray);">
                            <span>Progression</span>
                            <span>${progress.toFixed(1)}%</span>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <button style="
                            background: linear-gradient(135deg, ${team.color} 0%, ${team.color}80 100%);
                            border: none;
                            color: white;
                            padding: 10px 20px;
                            border-radius: 25px;
                            font-weight: 600;
                            cursor: pointer;
                            transition: all 0.3s;
                        " onmouseover="this.style.transform='translateY(-2px)'" 
                        onmouseout="this.style.transform='translateY(0)'">
                            Voir Dashboard ${team.name}
                        </button>
                    </div>
                `;
                
                teamsGrid.appendChild(teamCard);
            });
        }
        
        // Particules animées
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            const particleCount = 50;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.style.position = 'absolute';
                particle.style.width = Math.random() * 5 + 2 + 'px';
                particle.style.height = particle.style.width;
                particle.style.background = 'rgba(255, 255, 255, 0.1)';
                particle.style.borderRadius = '50%';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.opacity = Math.random() * 0.5 + 0.1;
                
                // Animation
                particle.animate([
                    { transform: 'translateY(0px)' },
                    { transform: `translateY(${Math.random() * 100 - 50}px)` }
                ], {
                    duration: Math.random() * 3000 + 2000,
                    iterations: Infinity,
                    direction: 'alternate'
                });
                
                particlesContainer.appendChild(particle);
            }
        }
        
        // Conseils aléatoires
        const tips = [
            "💡 Utilisez les QR codes pour un accès rapide aux fiches clients",
            "🚀 Complétez 5 installations pour débloquer le badge 'Équipe du Jour'",
            "📱 Téléchargez l'application mobile pour un suivi en temps réel",
            "🎯 Fixez-vous un objectif quotidien pour booster votre productivité",
            "🤝 Collaborez avec les autres équipes pour partager les meilleures pratiques",
            "📊 Consultez vos stats quotidiennes pour suivre votre progression",
            "⭐ Obtenez 3 étoiles en complétant les installations dans les délais",
            "🔔 Activez les notifications pour ne rien manquer des mises à jour"
        ];
        
        function showRandomTip() {
            const tip = tips[Math.floor(Math.random() * tips.length)];
            console.log('%c' + tip, 'color: #3b82f6; font-weight: bold; font-size: 14px;');
        }
        
        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {
            initStats();
            generateTeamCards();
            createParticles();
            showRandomTip();
            
            // Animation d'entrée
            const cards = document.querySelectorAll('.team-card, .stat-card, .fun-card');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
                setTimeout(() => {
                    card.style.transition = 'all 0.6s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
            
            // Mise à jour en temps réel (simulation)
            setInterval(() => {
                const successRate = document.getElementById('successRate');
                const currentRate = parseInt(successRate.textContent);
                const newRate = Math.min(100, currentRate + (Math.random() > 0.5 ? 1 : -1));
                successRate.textContent = newRate + '%';
            }, 5000);
        });
        
        // Effet de saisie pour les stats
        function animateCounter(element, target) {
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                element.textContent = formatNumber(Math.floor(current));
            }, 30);
        }
        
        // Animer les compteurs au chargement
        setTimeout(() => {
            const totalInstallations = teamsData.reduce((sum, team) => sum + team.installations, 0);
            animateCounter(document.getElementById('totalInstallations'), totalInstallations);
        }, 500);
    </script>
</body>
</html>"""
    
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    console.print("[green]✅ Dashboard générique créé : dashboard.html[/green]")

# Appelle cette fonction dans update_dashboards() ou main()
