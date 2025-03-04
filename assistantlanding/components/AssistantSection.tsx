"use client";
import { motion } from "framer-motion";
import { WaveformIcon, PulseIcon, CircleIcon } from "./AnimatedIcons";

const orbitVariants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 20,
      repeat: Infinity,
      ease: "linear",
    },
  },
};

const floatingVariants = {
  animate: {
    y: [-10, 10, -10],
    transition: {
      duration: 4,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

export default function AssistantSection() {
  return (
    <section className="container px-4 py-32 mx-auto relative">
      <div className="max-w-4xl mx-auto relative">
        <motion.div
          className="absolute inset-0"
          variants={orbitVariants}
          animate="animate"
        >
          {[...Array(8)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute"
              style={{
                transform: `rotate(${i * 45}deg) translateX(200px)`,
                transformOrigin: "center center",
              }}
              variants={floatingVariants}
              animate="animate"
              custom={i}
            >
              {i % 3 === 0 ? (
                <WaveformIcon />
              ) : i % 3 === 1 ? (
                <PulseIcon />
              ) : (
                <CircleIcon />
              )}
            </motion.div>
          ))}
        </motion.div>

        <div className="text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 0.8,
              type: "spring",
              stiffness: 100,
            }}
            className="relative inline-block"
          >
            <div className="absolute -inset-4 bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 rounded-full opacity-20 blur-xl" />
            <h2 className="text-6xl md:text-8xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500">
              Assistant
            </h2>
          </motion.div>

          <motion.div
            className="absolute -top-8 -right-8"
            animate={{ y: [-5, 5, -5], rotate: [0, 10, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          >
            <PulseIcon />
          </motion.div>
          <motion.div
            className="absolute -bottom-8 -left-8"
            animate={{ y: [5, -5, 5], rotate: [0, -10, 0] }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 1,
            }}
          >
            <WaveformIcon />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
