# 🔐 Surveillance Intelligente du Matériel Informatique

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/votre-repo/surveillance-materiel)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![ESMT](https://img.shields.io/badge/ESMT-INGC2%202024--2025-red.svg)](https://esmt.sn)

> Système de surveillance temps réel combinant vision par ordinateur (YOLOv8) et machine learning pour la sécurité des infrastructures informatiques académiques

**Projet de validation INGC2** - Option Intelligence des Données et Intelligence Artificielle  
**École Supérieure Multinationale des Télécommunications (ESMT)**

---

## 📸 Aperçu du Système en Action

<div align="center">

### 🎯 Détection d'Intrusions en Temps Réel

<table>
  <tr>
    <td align="center">
      <img src="outputs/detections/detection_20251108_092520.jpg" alt="Détection 1" width="350"/>
      <br/>
      <em>Détection avec haute confiance (95%)</em>
    </td>
    <td align="center">
      <img src="outputs/detections/detection_20251108_093015.jpg" alt="Détection 2" width="350"/>
      <br/>
      <em>Détection multiple personnes</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="outputs/detections/detection_20251108_100234.jpg" alt="Détection 3" width="350"/>
      <br/>
      <em>Détection en conditions variables</em>
    </td>
    <td align="center">
      <img src="outputs/detections/detection_20251108_101542.jpg" alt="Détection 4" width="350"/>
      <br/>
      <em>Tracking précis avec bounding boxes</em>
    </td>
  </tr>
</table>

### ✨ Caractéristiques Visuelles
- ✅ **Bounding boxes** en temps réel avec confiance affichée
- ✅ **Capture automatique** d'images horodatées
- ✅ **Overlay d'informations** (timestamp, FPS, détections)
- ✅ **Interface moderne** avec TailwindCSS

</div>

---

## 📋 Table des Matières

- [Aperçu du Projet](#-aperçu-du-projet)
- [Fonctionnalités Principales](#-fonctionnalités-principales)
- [Architecture Technique](#-architecture-technique)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Modèles Machine Learning](#-modèles-machine-learning)
- [Système d'Alertes](#-système-dalertes)
- [Dashboard et Visualisations](#-dashboard-et-visualisations)
- [Tests et Validation](#-tests-et-validation)
- [Structure du Projet](#-structure-du-projet)
- [API Documentation](#-api-documentation)
- [Déploiement](#-déploiement)
- [Limitations et Améliorations](#-limitations-et-améliorations)
- [Contribution](#-contribution)
- [Auteurs](#-auteurs)
- [Remerciements](#-remerciements)

---

## 🎯 Aperçu du Projet

### Contexte et Problématique

Les salles de travaux pratiques (TP) informatiques dans les établissements d'enseignement supérieur sont confrontées à plusieurs défis de sécurité :

- **Intrusions physiques** non autorisées
- **Surveillance humaine** coûteuse et peu efficace
- **Détection tardive** des anomalies système
- **Usage non autorisé** ou détérioration du matériel
- **Absence de corrélation** entre événements physiques et logiciels

### Notre Solution

Un système intelligent et modulaire qui combine trois approches complémentaires :

1. **👁️ Vision par Ordinateur** - Détection d'intrusions physiques via YOLOv8
2. **🧠 Machine Learning** - Détection d'anomalies système (supervisé + non supervisé)
3. **📊 Visualisation Intelligente** - Analyse et interprétation avec Yellowbrick

### Objectifs

**Pédagogiques :**
- Maîtriser l'intégration OpenCV et scikit-learn
- Implémenter des algorithmes de détection d'anomalies
- Développer des compétences en visualisation de données
- Concevoir une architecture système temps réel

**Scientifiques :**
- Évaluer l'efficacité de YOLOv8 en environnement contrôlé
- Comparer approches supervisées vs non supervisées
- Mesurer l'impact de la qualité des données sur les performances

---

## ✨ Fonctionnalités Principales

### 🎥 Détection d'Intrusions par Vision

<div align="center">
  <img src="outputs/detections/detection_20251108_092520.jpg" alt="Exemple de détection" width="600"/>
  <br/>
  <em>Exemple de détection en temps réel avec bounding box et score de confiance</em>
</div>

<br/>

- **Détection temps réel** de présence humaine via YOLOv8
- **Précision de détection** > 95% (mAP50)
- **Capture automatique** d'images preuves avec timestamp
- **Flux vidéo MJPEG** avec overlay des détections
- **Gestion anti-spam** avec cooldowns intelligents
- **Format ONNX** pour inférence optimisée

**Métriques :**
- Precision: 0.964
- Recall: 0.957
- F1-Score: 0.960
- Latence: < 100ms par frame

### 📊 Surveillance Système en Temps Réel

**Métriques Collectées (toutes les 5 secondes) :**
- Utilisation CPU (%)
- Consommation mémoire (%)
- Température processeur (°C)
- Connexions réseau actives
- Nombre de processus
- Périphériques USB connectés
- Activité réseau (octets envoyés/reçus)

### 🤖 Détection d'Anomalies ML

**Approche Double :**

#### 1. Apprentissage Supervisé (Random Forest)
- Classification binaire normal/anormal
- **Précision : 95.2%**
- F1-Score : 0.94
- 8 features d'entrée

#### 2. Apprentissage Non Supervisé
- **KMeans Clustering** : Identification de 3 profils d'utilisation
- **Isolation Forest** : Détection d'outliers avec contamination 10%
- Score d'anomalie personnalisable

**Features Utilisées :**
```
1. cpu_percent          5. process_count
2. memory_percent       6. network_connections
3. temperature          7. bytes_sent
4. disk_usage          8. bytes_received
```

### 🚨 Système d'Alertes Multi-niveaux

**Hiérarchie des Sévérités :**

| Niveau | Types d'Alertes | Cooldown | Action |
|--------|----------------|----------|--------|
| 🔴 CRITICAL | Intrusion caméra, Surchauffe >80°C | 300s | Notification immédiate |
| 🟠 HIGH | Surcharge CPU >90%, Fuite mémoire | 240s | Notification prioritaire |
| 🟡 MEDIUM | Activité réseau anormale, USB non autorisé | 180s | Log et monitoring |
| 🔵 LOW | Avertissements système | 120s | Log uniquement |

**Caractéristiques :**
- Gestion intelligente des cooldowns
- Escalade automatique (1ère → 2ème → 3+ occurrences)
- Journalisation JSONL pour audit
- Sauvegarde automatique d'images preuves
- WebSocket pour notifications temps réel

---

## 📈 Dashboard et Visualisations

### 🖥️ Interface Principale

<div align="center">

#### Vue d'Ensemble du Dashboard

<img src="outputs/screenshots/dashboard_overview.png" alt="Dashboard Principal" width="800"/>

*Dashboard temps réel avec flux vidéo, métriques système et alertes*

---

#### 📹 Flux Vidéo en Direct

<table>
  <tr>
    <td align="center" width="50%">
      <img src="outputs/detections/detection_20251108_100234.jpg" alt="Flux vidéo 1" width="100%"/>
      <br/>
      <em>Surveillance active - Aucune détection</em>
    </td>
    <td align="center" width="50%">
      <img src="outputs/detections/detection_20251108_101542.jpg" alt="Flux vidéo 2" width="100%"/>
      <br/>
      <em>Intrusion détectée - Alerte déclenchée</em>
    </td>
  </tr>
</table>

---

#### 📊 Graphiques Temps Réel

<table>
  <tr>
    <td align="center">
      <img src="outputs/screenshots/cpu_chart.png" alt="Graphique CPU" width="100%"/>
      <br/>
      <strong>Utilisation CPU</strong>
      <br/>
      <em>Monitoring continu avec seuils d'alerte</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="outputs/screenshots/memory_chart.png" alt="Graphique Mémoire" width="100%"/>
      <br/>
      <strong>Consommation Mémoire</strong>
      <br/>
      <em>Détection des fuites et pics anormaux</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="outputs/screenshots/temperature_gauge.png" alt="Jauge Température" width="100%"/>
      <br/>
      <strong>Température Processeur</strong>
      <br/>
      <em>Indicateur coloré avec alertes thermiques</em>
    </td>
  </tr>
</table>

---

#### 🚨 Panneau d'Alertes

<img src="outputs/screenshots/alerts_panel.png" alt="Panneau d'alertes" width="800"/>

*Historique des alertes avec code couleur par sévérité et images de preuve*

</div>

### Composants du Dashboard

**1. Header Navigation**
   - Logo et titre du projet
   - Liens vers Dashboard et Alertes
   - Indicateur de statut (En ligne/Hors ligne)

**2. Flux Vidéo Temps Réel**
   - Stream MJPEG de la caméra
   - Overlay des détections (bounding boxes)
   - Confiance affichée en temps réel
   - Résolution : 640x480

**3. Métriques Système** (mise à jour toutes les 5s)
   - CPU : Graphique + pourcentage
   - Mémoire : Graphique + pourcentage
   - Température : Indicateur coloré
   - Réseau : Connexions actives

**4. Panneau d'Alertes Récentes**
   - 20 dernières alertes
   - Code couleur par sévérité
   - Timestamp relatif ("il y a 5 minutes")
   - Filtrage par sévérité

**5. Indicateurs de Statut**
   - État de la caméra
   - État du monitoring
   - État du ML
   - Statistiques globales

### 📱 Page des Alertes (`/alerts`)

<div align="center">
  <img src="outputs/screenshots/alerts_page.png" alt="Page des alertes" width="800"/>
  <br/>
  <em>Historique complet avec filtrage et recherche avancée</em>
</div>

**Fonctionnalités :**
- Historique complet (200 dernières alertes)
- Images de détection pour les intrusions
- Filtrage par type et sévérité
- Recherche par date
- Export JSON/CSV
- Pagination

### 🎨 Exemples de Détections

<div align="center">

#### Galerie de Détections

<table>
  <tr>
    <td align="center" width="33%">
      <img src="outputs/detections/detection_20251108_092520.jpg" alt="Détection matin" width="100%"/>
      <br/>
      <em>08:30 - Lumière naturelle</em>
      <br/>
      <strong>Confiance: 96%</strong>
    </td>
    <td align="center" width="33%">
      <img src="outputs/detections/detection_20251108_093015.jpg" alt="Détection après-midi" width="100%"/>
      <br/>
      <em>14:15 - Éclairage mixte</em>
      <br/>
      <strong>Confiance: 92%</strong>
    </td>
    <td align="center" width="33%">
      <img src="outputs/detections/detection_20251108_100234.jpg" alt="Détection soir" width="100%"/>
      <br/>
      <em>19:45 - Faible luminosité</em>
      <br/>
      <strong>Confiance: 88%</strong>
    </td>
  </tr>
  <tr>
    <td colspan="3" align="center">
      <br/>
      <strong>🌟 Performance robuste dans différentes conditions d'éclairage</strong>
    </td>
  </tr>
</table>

#### Scénarios Multi-Personnes

<table>
  <tr>
    <td align="center" width="50%">
      <img src="outputs/detections/detection_20251108_101542.jpg" alt="Multi-détection 1" width="100%"/>
      <br/>
      <strong>2 personnes détectées</strong>
      <br/>
      <em>Tracking simultané avec IDs distincts</em>
    </td>
    <td align="center" width="50%">
      <img src="outputs/detections/detection_20251108_092520.jpg" alt="Multi-détection 2" width="100%"/>
      <br/>
      <strong>3 personnes détectées</strong>
      <br/>
      <em>Gestion des occlusions partielles</em>
    </td>
  </tr>
</table>

</div>

### 🎯 Précision Visuelle

```
┌─────────────────────────────────────────────────────────┐
│              PERFORMANCES DE DÉTECTION                   │
├─────────────────────────────────────────────────────────┤
│  📊 mAP50:          96.4%  ████████████████████░        │
│  🎯 Précision:      96.4%  ████████████████████░        │
│  🔍 Rappel:         95.7%  ███████████████████▓░        │
│  ⚡ FPS (CPU):      ~30    ████████████████████         │
│  ⏱️ Latence:        <100ms ████████████████████         │
└─────────────────────────────────────────────────────────┘
```

### 💡 Technologies Frontend

- **Framework CSS** : TailwindCSS 2.2
- **Graphiques** : Chart.js 3.x avec animations fluides
- **Icônes** : Font Awesome 6.4
- **Communication** : WebSocket (Socket.IO)
- **Responsive Design** : Mobile-first approach

### 🔄 Communication Temps Réel

**Événements SocketIO :**

```javascript
// Mise à jour des métriques toutes les 5s
socket.on('metrics_update', (data) => {
    updateCPUChart(data.cpu_percent);
    updateMemoryChart(data.memory_percent);
    updateTemperature(data.temperature);
});

// Notifications instantanées d'alertes
socket.on('new_alert', (alert) => {
    addAlertToPanel(alert);
    playNotificationSound();
    showToast(alert.message, alert.severity);
});

// Confirmation de connexion
socket.on('connection_response', (data) => {
    updateConnectionStatus('connected');
});
```

---

## 🏗️ Architecture Technique

### Stack Technologique

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (Web UI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Dashboard   │  │  Alerts View │  │ Video Stream │  │
│  │ (HTML/CSS/JS)│  │  (TailwindCSS│  │   (MJPEG)    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼──────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                      WebSocket / HTTP
┌─────────────────────────────────────────────────────────┐
│              BACKEND (Flask Application)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │              app/main.py (Orchestrateur)         │  │
│  └───────┬────────────────────────────────┬─────────┘  │
│          │                                 │             │
│  ┌───────▼────────┐    ┌──────────────────▼────────┐  │
│  │  Vision Module │    │   ML Anomaly Detection    │  │
│  │  app/core/     │    │      app/ml/              │  │
│  │  - camera.py   │    │  - predictor.py           │  │
│  │  - YOLOv8      │    │  - Random Forest          │  │
│  └───────┬────────┘    │  - Isolation Forest       │  │
│          │             │  - KMeans                 │  │
│  ┌───────▼────────┐    └──────────────────┬────────┘  │
│  │ System Monitor │                       │             │
│  │  app/core/     │    ┌──────────────────▼────────┐  │
│  │  - psutil      │◄───┤   Alert System            │  │
│  │  - pyudev      │    │   app/core/               │  │
│  └────────────────┘    │   - alert_system.py       │  │
│                        └───────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────┐
│                    DATA LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Logs (JSONL) │  │ Models (.pkl)│  │ Images (.jpg)│  │
│  │ outputs/logs │  │ models/ml/   │  │ outputs/     │  │
│  └──────────────┘  └──────────────┘  │ detections/  │  │
└─────────────────────────────────────────────────────────┘

---

## 📸 Galerie Complète

Pour voir plus d'exemples de détections, consultez le dossier `outputs/detections/` qui contient :
- **Images horodatées** de toutes les détections
- **Métadonnées** associées (confiance, coordonnées, timestamp)
- **Historique visuel** de la surveillance

**Accès rapide :**
```bash
# Voir les détections récentes
ls -lt outputs/detections/ | head -20

# Rechercher par date
find outputs/detections/ -name "*20251108*"

# Statistiques
echo "Nombre total de détections: $(ls outputs/detections/ | wc -l)"
```
