"use client";
import { motion } from "framer-motion";

export default function WaveAnimation() {
  const waveVariants = {
    animate: {
      y: [0, -20, 0],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut",
      },
    },
  };

  return (
    <div className="relative w-full h-48 overflow-hidden">
      {[...Array(3)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-full h-48"
          style={{
            background: `rgba(147, 197, 253, ${0.1 + i * 0.1})`,
            borderRadius: "50%",
            scale: 1.5 + i * 0.2,
          }}
          variants={waveVariants}
          animate="animate"
          custom={i}
          initial="initial"
        />
      ))}
    </div>
  );
}
