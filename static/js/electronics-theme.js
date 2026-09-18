/**
 * Electronics Theme JavaScript
 * Advanced interactions for Wafer Fault Detection System
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize theme
    initializeElectronicsTheme();
    
    // Add interactive elements
    addInteractiveEffects();
    
    // Initialize system status monitoring
    initializeSystemMonitoring();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
});

function initializeElectronicsTheme() {
    console.log('🔧 Initializing Electronics Theme...');
    
    // Add circuit animation to hero section
    addCircuitAnimation();
    
    // Initialize particle system
    initializeParticles();
    
    // Add typing effect to title
    addTypingEffect();
}

function addCircuitAnimation() {
    // Create animated circuit lines
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        const canvas = document.createElement('canvas');
        canvas.className = 'circuit-canvas position-absolute top-0 start-0 w-100 h-100';
        canvas.style.zIndex = '0';
        canvas.style.opacity = '0.1';
        heroSection.appendChild(canvas);
        
        // Simple circuit animation
        animateCircuit(canvas);
    }
}

function animateCircuit(canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    const nodes = [];
    const connections = [];
    
    // Create nodes
    for (let i = 0; i < 20; i++) {
        nodes.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            pulse: Math.random() * Math.PI * 2
        });
    }
    
    // Create connections
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            const distance = Math.sqrt(
                Math.pow(nodes[i].x - nodes[j].x, 2) + 
                Math.pow(nodes[i].y - nodes[j].y, 2)
            );
            if (distance < 150) {
                connections.push({ from: i, to: j, distance });
            }
        }
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw connections
        connections.forEach(conn => {
            const fromNode = nodes[conn.from];
            const toNode = nodes[conn.to];
            
            ctx.beginPath();
            ctx.moveTo(fromNode.x, fromNode.y);
            ctx.lineTo(toNode.x, toNode.y);
            ctx.strokeStyle = `rgba(0, 204, 255, ${0.3 - conn.distance / 500})`;
            ctx.lineWidth = 1;
            ctx.stroke();
        });
        
        // Draw nodes
        nodes.forEach(node => {
            node.pulse += 0.05;
            const pulseSize = 2 + Math.sin(node.pulse) * 1;
            
            ctx.beginPath();
            ctx.arc(node.x, node.y, pulseSize, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 255, 136, ${0.6 + Math.sin(node.pulse) * 0.4})`;
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

function initializeParticles() {
    // Add floating particles effect
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-container position-fixed top-0 start-0 w-100 h-100';
    particleContainer.style.zIndex = '-1';
    particleContainer.style.pointerEvents = 'none';
    document.body.appendChild(particleContainer);
    
    for (let i = 0; i < 50; i++) {
        createParticle(particleContainer);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.cssText = `
        position: absolute;
        width: 2px;
        height: 2px;
        background: rgba(0, 204, 255, 0.6);
        border-radius: 50%;
        animation: float ${5 + Math.random() * 10}s linear infinite;
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        box-shadow: 0 0 6px rgba(0, 204, 255, 0.8);
    `;
    
    container.appendChild(particle);
    
    // Remove and recreate particle after animation
    setTimeout(() => {
        if (particle.parentNode) {
            particle.parentNode.removeChild(particle);
            createParticle(container);
        }
    }, (5 + Math.random() * 10) * 1000);
}

function addTypingEffect() {
    const titleElement = document.querySelector('.hero-section .display-4 .text-gradient');
    if (titleElement) {
        const originalText = titleElement.textContent;
        titleElement.textContent = '';
        
        let i = 0;
        const typeInterval = setInterval(() => {
            titleElement.textContent += originalText.charAt(i);
            i++;
            if (i >= originalText.length) {
                clearInterval(typeInterval);
                titleElement.classList.add('glitch-effect');
            }
        }, 100);
    }
}

function addInteractiveEffects() {
    // Add hover effects to cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
            this.style.boxShadow = '0 15px 40px rgba(0, 204, 255, 0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
    });
    
    // Add click ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add CSS for ripple animation
    if (!document.querySelector('#ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

function initializeSystemMonitoring() {
    // Simulate real-time system monitoring
    const statusIndicators = document.querySelectorAll('.status-indicator.online');
    
    statusIndicators.forEach(indicator => {
        setInterval(() => {
            indicator.style.opacity = indicator.style.opacity === '0.5' ? '1' : '0.5';
        }, 1000 + Math.random() * 1000);
    });
    
    // Add system stats animation
    animateSystemStats();
}

function animateSystemStats() {
    const statNumbers = document.querySelectorAll('.h3');
    
    statNumbers.forEach(stat => {
        const finalValue = parseInt(stat.textContent);
        if (!isNaN(finalValue)) {
            let currentValue = 0;
            const increment = finalValue / 50;
            
            const counter = setInterval(() => {
                currentValue += increment;
                if (currentValue >= finalValue) {
                    stat.textContent = finalValue;
                    clearInterval(counter);
                } else {
                    stat.textContent = Math.floor(currentValue);
                }
            }, 50);
        }
    });
}

function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + U: Upload page
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            window.location.href = '/upload';
        }
        
        // Ctrl/Cmd + D: Dashboard
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            window.location.href = '/dashboard';
        }
        
        // Ctrl/Cmd + S: System Status
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            window.location.href = '/system_status';
        }
        
        // Escape: Home
        if (e.key === 'Escape') {
            window.location.href = '/';
        }
    });
    
    // Show keyboard shortcuts hint
    setTimeout(() => {
        if (localStorage.getItem('keyboard-hints-shown') !== 'true') {
            showKeyboardHints();
            localStorage.setItem('keyboard-hints-shown', 'true');
        }
    }, 3000);
}

function showKeyboardHints() {
    const hint = document.createElement('div');
    hint.className = 'keyboard-hint position-fixed bottom-0 end-0 m-3 p-3 bg-dark text-light rounded';
    hint.style.zIndex = '9999';
    hint.innerHTML = `
        <div class="d-flex align-items-center mb-2">
            <i class="fas fa-keyboard me-2"></i>
            <strong>Keyboard Shortcuts</strong>
            <button class="btn-close btn-close-white ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
        <small>
            <div>Ctrl+U: Upload</div>
            <div>Ctrl+D: Dashboard</div>
            <div>Ctrl+S: System Status</div>
            <div>Esc: Home</div>
        </small>
    `;
    
    document.body.appendChild(hint);
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        if (hint.parentNode) {
            hint.remove();
        }
    }, 10000);
}

// Add console welcome message
console.log(`
🔬 Wafer Fault Detection System
🤖 AI-Powered Electronics Engineering
⚡ Advanced Theme Loaded Successfully

Keyboard Shortcuts:
• Ctrl+U: Upload & Analyze
• Ctrl+D: Analytics Dashboard  
• Ctrl+S: System Status
• Esc: Home

System Status: ✅ Online
Models: XGBoost (97.49%) + Random Forest (94.72%)
Features: 282 sensors across 10 categories
`);

// Export functions for global access
window.ElectronicsTheme = {
    initializeElectronicsTheme,
    addInteractiveEffects,
    initializeSystemMonitoring,
    addKeyboardShortcuts
};
