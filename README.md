# OpenRouteService (ORS) Backend - Jakarta/Java

A complete OpenRouteService backend setup with routing, isochrones, matrix, and snap services for Jakarta and Java island region. Includes a Streamlit web interface for testing and demonstration.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM (12GB+ recommended for multiple profiles)
- 10GB+ free disk space

### 1. Clone & Setup
```bash
gh repo clone azizrh/ORS-config
cd newORS
```

### 2. Download OSM Data
```bash
# Download Java island OSM data (~500MB)
wget https://download.geofabrik.de/asia/indonesia/java-latest.osm.pbf -O ors-docker/files/java-latest.osm.pbf

# Alternative: Manual download
# Visit: https://download.geofabrik.de/asia/indonesia.html
# Download java-latest.osm.pbf to ors-docker/files/
```

### 3. Start ORS
```bash
# Start ORS backend
docker-compose up -d

# Monitor graph building progress (takes 1-3 hours)
docker-compose logs -f ors-app
```

### 4. Access Services
- **ORS API**: http://localhost:8080/ors/v2/
- **Health Check**: http://localhost:8080/ors/v2/health
- **API Status**: http://localhost:8080/ors/v2/status

## 📋 Available Services

### 🗺️ Routing Profiles
- **🚗 driving-car** - Car navigation
- **🚶 foot-walking** - Pedestrian routing
- **🚴 cycling-regular** - Bicycle routing

### 🔧 API Endpoints
- **Directions**: `/v2/directions/{profile}` - Route planning A to B
- **Isochrones**: `/v2/isochrones/{profile}` - Reachability areas
- **Matrix**: `/v2/matrix/{profile}` - Distance/time matrices
- **Snap**: `/v2/snap/{profile}` - Snap coordinates to roads

## 🌐 Streamlit Web Interface

### Setup Python Environment
```bash
# Create virtual environment
python -m venv env
source env/bin/activate  # Linux/Mac
# or
env\Scripts\activate     # Windows

# Install dependencies
pip install streamlit folium streamlit-folium pandas plotly requests polyline
```

### Run Web Interface
```bash
# Start Streamlit app
streamlit run ors_streamlit_app.py

# Access at: http://localhost:8501
```

### Share with ngrok
```bash
# Install ngrok
sudo snap install ngrok

# Setup auth token (free account required)
ngrok config add-authtoken YOUR_TOKEN

# Share publicly
ngrok http 8501
```

## 🔧 Configuration

### Memory Settings
Update `docker-compose.yml` for your system:
```yaml
environment:
  XMS: 2g      # Start memory
  XMX: 8g      # Max memory (adjust based on your RAM)
```

### Adding More Profiles
Edit `ors-docker/config/ors-config.yml`:
```yaml
profiles:
  # Uncomment to enable additional profiles
  hgv:
    enabled: true
    build: true
    profile: driving-hgv
  wheelchair:
    enabled: true
    build: true
    profile: wheelchair
```

Then rebuild:
```bash
docker-compose down
sudo rm -rf ors-docker/graphs/*  # Clear existing graphs
docker-compose up -d
```

## 📊 Usage Examples

### 1. Basic Routing
```bash
# Get route from Blok M to Kolam Renang Bulungan
curl "http://localhost:8080/ors/v2/directions/driving-car?start=106.8006,-6.2446&end=106.7932,-6.2409"
```

### 2. Isochrones (Reachability Areas)
```bash
# 15-minute driving range from Blok M
curl -X POST "http://localhost:8080/ors/v2/isochrones/driving-car" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": [[106.8006,-6.2446]],
    "range": [900]
  }'
```

### 3. Distance Matrix
```bash
# Distance/time between multiple points
curl -X POST "http://localhost:8080/ors/v2/matrix/driving-car" \
  -H "Content-Type: application/json" \
  -d '{
    "locations": [
      [106.8006,-6.2446],
      [106.7932,-6.2409],
      [106.8200,-6.2100]
    ]
  }'
```

## 🏙️ Default Jakarta Locations

The setup includes preconfigured Jakarta coordinates:
- **Blok M Square**: -6.2446, 106.8006
- **Kolam Renang Bulungan**: -6.2409, 106.7932
- **Senayan Area**: -6.2350, 106.8100
- **Sudirman District**: -6.2100, 106.8200

## 🛠️ Troubleshooting

### Graph Building Issues
```bash
# Check logs for errors
docker-compose logs ors-app | grep -i error

# Check memory usage
docker stats ors-app

# Restart if needed
docker-compose restart
```

### Memory Issues
- **Out of Memory (Code 137)**: Increase XMX in docker-compose.yml
- **WSL Users**: Configure `.wslconfig` with more memory
- **Swap Space**: Enable swap if system memory is limited

### API Issues
```bash
# Check if ORS is ready
curl http://localhost:8080/ors/v2/health

# Check available profiles
curl http://localhost:8080/ors/v2/status

# Test basic routing
curl "http://localhost:8080/ors/v2/directions/driving-car?start=106.8006,-6.2446&end=106.8010,-6.2450"
```

## 📁 Project Structure

```
newORS/
├── docker-compose.yml              # Docker configuration
├── ors-docker/
│   ├── config/
│   │   └── ors-config.yml         # ORS configuration
│   ├── files/
│   │   └── java-latest.osm.pbf    # OSM data (download required)
│   ├── graphs/                    # Built routing graphs (generated)
│   ├── logs/                      # Application logs
│   └── elevation_cache/           # Elevation data cache
├── ors_streamlit_app.py           # Streamlit web interface
├── README.md                      # This file
└── .gitignore                     # Git ignore rules
```

## 📚 Advanced Usage

### Custom Areas
Edit `ors-config.yml` to focus on specific regions:
```yaml
encoder_options:
  maximum_distance: 50000  # Limit routing distance
  block_fords: false       # Allow/block water crossings
```

### Optimization Service
For vehicle routing problems (VRP/TSP), install VROOM:
```bash
# Run VROOM separately
docker run -d --name vroom-engine -p 3000:3000 vroomvrp/vroom-docker
```

### Performance Tuning
```yaml
# In ors-config.yml
preparation:
  methods:
    ch:
      enabled: true
      threads: 2          # Increase for faster building
      weightings: fastest
```

## 🔒 Security Notes

- **Local Development Only**: Default setup is for local use
- **Production Deployment**: Configure proper firewall rules
- **API Rate Limiting**: Consider adding rate limiting for public use
- **Authentication**: Add authentication for sensitive deployments

## 🆘 Support

### Resources
- **ORS Documentation**: https://giscience.github.io/openrouteservice/
- **API Reference**: https://openrouteservice.org/dev/#/api-docs
- **OSM Data**: https://download.geofabrik.de/asia/indonesia.html

### Common Solutions
- **Slow Performance**: Increase memory allocation
- **Missing Routes**: Check if coordinates are in Jakarta/Java area
- **Build Failures**: Ensure sufficient disk space and memory
- **Connection Issues**: Verify Docker is running and ports are open

## 📄 License

This project uses OpenRouteService which is licensed under GPL v3. OSM data is © OpenStreetMap contributors.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

---

**Built with ❤️ for Jakarta routing and navigation**