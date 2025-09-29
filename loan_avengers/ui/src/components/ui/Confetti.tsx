import { useEffect, useState } from 'react';

const CONFETTI_EMOJIS = ['🎉', '🎊', '✨', '💎', '🏆', '⭐', '🥳', '🎈', '💰', '🏠', '✅', '🌟'];

interface ConfettiParticle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  rotation: number;
  rotationSpeed: number;
  emoji: string;
  size: number;
  opacity: number;
}

interface ConfettiProps {
  active?: boolean;
  count?: number;
  duration?: number;
}

/**
 * Confetti animation component for celebration effects
 * Creates emoji-based particles that fall from the top of the screen with physics
 */
export function Confetti({ active = false, count = 100, duration = 5000 }: ConfettiProps) {
  const [particles, setParticles] = useState<ConfettiParticle[]>([]);

  useEffect(() => {
    if (!active) {
      setParticles([]);
      return;
    }

    // Create initial particles
    const newParticles: ConfettiParticle[] = [];
    for (let i = 0; i < count; i++) {
      newParticles.push({
        id: i,
        x: Math.random() * window.innerWidth,
        y: -20 - Math.random() * 100, // Start above viewport with stagger
        vx: (Math.random() - 0.5) * 8, // Horizontal velocity
        vy: Math.random() * 3 + 2, // Initial downward velocity
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 10,
        emoji: CONFETTI_EMOJIS[Math.floor(Math.random() * CONFETTI_EMOJIS.length)],
        size: Math.random() * 20 + 15, // Size between 15-35px
        opacity: 1,
      });
    }
    setParticles(newParticles);

    // Physics-based animation loop
    let animationId: number;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = elapsed / duration;

      if (progress >= 1) {
        setParticles([]);
        return;
      }

      setParticles((current) =>
        current.map((particle) => ({
          ...particle,
          x: particle.x + particle.vx,
          y: particle.y + particle.vy,
          rotation: particle.rotation + particle.rotationSpeed,
          vy: particle.vy + 0.3, // Gravity acceleration
          vx: particle.vx * 0.99, // Air resistance
          opacity: Math.max(0, 1 - progress * 0.8), // Fade out towards end
        })).filter((particle) =>
          particle.y < window.innerHeight + 50 &&
          particle.opacity > 0.1 &&
          particle.x > -50 &&
          particle.x < window.innerWidth + 50
        )
      );

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [active, count, duration]);

  if (!active || particles.length === 0) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 pointer-events-none z-50 overflow-hidden"
      aria-hidden="true"
      role="presentation"
    >
      {particles.map((particle) => (
        <div
          key={particle.id}
          className="absolute transition-none select-none"
          style={{
            left: `${particle.x}px`,
            top: `${particle.y}px`,
            transform: `rotate(${particle.rotation}deg)`,
            fontSize: `${particle.size}px`,
            opacity: particle.opacity,
            willChange: 'transform, opacity',
            pointerEvents: 'none',
          }}
        >
          {particle.emoji}
        </div>
      ))}
    </div>
  );
}