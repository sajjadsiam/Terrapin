#!/bin/bash
# Terrapin Attack Lab - Setup and Run Script

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║           TERRAPIN ATTACK - DEMO LAB SETUP                ║
║                   CVE-2023-48795                          ║
║                                                            ║
║              ⚠️  EDUCATIONAL USE ONLY ⚠️                   ║
╚════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}[*] Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[!] Docker is not installed${NC}"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}[✓] Docker found${NC}"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}[!] Docker Compose is not installed${NC}"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    echo -e "${GREEN}[✓] Docker Compose found${NC}"
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        echo -e "${RED}[!] Docker daemon is not running${NC}"
        echo "Please start Docker daemon"
        exit 1
    fi
    echo -e "${GREEN}[✓] Docker daemon running${NC}"
    
    echo ""
}

# Build the lab
build_lab() {
    echo -e "${YELLOW}[*] Building Docker containers...${NC}"
    echo "This may take a few minutes on first run..."
    echo ""
    
    docker-compose build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] Build completed successfully${NC}"
    else
        echo -e "${RED}[!] Build failed${NC}"
        exit 1
    fi
    echo ""
}

# Start the lab
start_lab() {
    echo -e "${YELLOW}[*] Starting containers...${NC}"
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] Containers started${NC}"
    else
        echo -e "${RED}[!] Failed to start containers${NC}"
        exit 1
    fi
    
    # Wait for containers to be ready
    echo -e "${YELLOW}[*] Waiting for services to be ready...${NC}"
    sleep 5
    
    echo ""
}

# Status check
check_status() {
    echo -e "${YELLOW}[*] Container status:${NC}"
    docker-compose ps
    echo ""
}

# Run vulnerability check
verify_vulnerability() {
    echo -e "${YELLOW}[*] Verifying vulnerability...${NC}"
    echo ""
    
    docker exec -it terrapin-attacker python3 /attack/demo/verify_vulnerability.py --host vulnerable-server --port 22
    
    echo ""
}

# Show next steps
show_next_steps() {
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Lab Setup Complete!                          ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo ""
    echo "1️⃣  Read the Quick Start Guide:"
    echo "   cat QUICKSTART.md"
    echo ""
    echo "2️⃣  Or jump right into the attack:"
    echo ""
    echo "   Terminal 1 (start attack proxy):"
    echo "   ${YELLOW}docker exec -it terrapin-attacker python3 /attack/poc_exploit/terrapin_exploit.py --target vulnerable-server --port 22 --proxy-port 2222${NC}"
    echo ""
    echo "   Terminal 2 (connect through proxy):"
    echo "   ${YELLOW}docker exec -it terrapin-client python3 /client/test_client.py --host attacker --port 2222${NC}"
    echo ""
    echo "3️⃣  For detailed walkthrough:"
    echo "   cat LAB_WALKTHROUGH.md"
    echo ""
    echo "4️⃣  To stop the lab:"
    echo "   docker-compose down"
    echo ""
    echo -e "${RED}⚠️  Remember: Educational use only!${NC}"
    echo ""
}

# Menu
show_menu() {
    echo -e "${BLUE}What would you like to do?${NC}"
    echo "1) Full setup (build + start + verify)"
    echo "2) Build only"
    echo "3) Start lab"
    echo "4) Check status"
    echo "5) Verify vulnerability"
    echo "6) Stop lab"
    echo "7) Stop and remove lab"
    echo "8) Show logs"
    echo "9) Exit"
    echo ""
    read -p "Enter choice [1-9]: " choice
}

# Main function
main() {
    print_banner
    
    # If no arguments, show interactive menu
    if [ $# -eq 0 ]; then
        check_prerequisites
        
        while true; do
            show_menu
            
            case $choice in
                1)
                    build_lab
                    start_lab
                    check_status
                    verify_vulnerability
                    show_next_steps
                    break
                    ;;
                2)
                    build_lab
                    ;;
                3)
                    start_lab
                    check_status
                    ;;
                4)
                    check_status
                    ;;
                5)
                    verify_vulnerability
                    ;;
                6)
                    echo -e "${YELLOW}[*] Stopping lab...${NC}"
                    docker-compose stop
                    ;;
                7)
                    echo -e "${YELLOW}[*] Stopping and removing lab...${NC}"
                    docker-compose down
                    ;;
                8)
                    echo "Which container? (vulnerable-server/attacker/client)"
                    read container
                    docker logs terrapin-$container
                    ;;
                9)
                    echo "Goodbye!"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}Invalid choice${NC}"
                    ;;
            esac
            echo ""
        done
    else
        # Command line arguments
        case $1 in
            build)
                check_prerequisites
                build_lab
                ;;
            start)
                start_lab
                check_status
                ;;
            stop)
                docker-compose stop
                ;;
            down)
                docker-compose down
                ;;
            status)
                check_status
                ;;
            verify)
                verify_vulnerability
                ;;
            setup)
                check_prerequisites
                build_lab
                start_lab
                check_status
                verify_vulnerability
                show_next_steps
                ;;
            *)
                echo "Usage: $0 [build|start|stop|down|status|verify|setup]"
                echo ""
                echo "Commands:"
                echo "  build   - Build Docker containers"
                echo "  start   - Start the lab"
                echo "  stop    - Stop the lab"
                echo "  down    - Stop and remove the lab"
                echo "  status  - Check container status"
                echo "  verify  - Verify vulnerability"
                echo "  setup   - Full setup (recommended for first time)"
                echo ""
                echo "Or run without arguments for interactive menu"
                exit 1
                ;;
        esac
    fi
}

# Run main function
main "$@"
