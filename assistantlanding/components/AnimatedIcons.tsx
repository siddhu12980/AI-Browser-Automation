import { motion } from "framer-motion";

export const WaveformIcon = () => {
  const waveVariants = {
    animate: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const lineVariants = {
    initial: { scaleY: 0.5 },
    animate: {
      scaleY: [0.5, 1, 0.5],
      transition: {
        repeat: Infinity,
        duration: 1,
        ease: "easeInOut",
      },
    },
  };

  return (
    <motion.svg
      width="50"
      height="50"
      viewBox="0 0 50 50"
      variants={waveVariants}
      animate="animate"
      className="text-primary"
    >
      {[...Array(5)].map((_, i) => (
        <motion.rect
          key={i}
          x={8 + i * 8}
          y="15"
          width="4"
          height="20"
          rx="2"
          fill="currentColor"
          variants={lineVariants}
          initial="initial"
        />
      ))}
    </motion.svg>
  );
};

export const PulseIcon = () => {
  return (
    <motion.div
      className="w-12 h-12 rounded-full bg-primary/20"
      animate={{
        scale: [1, 1.2, 1],
        opacity: [0.5, 1, 0.5],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      <motion.div
        className="w-8 h-8 rounded-full bg-primary/40 mx-auto mt-2"
        animate={{
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </motion.div>
  );
};

export const CircleIcon = () => {
  return (
    <motion.div
      className="relative w-12 h-12"
      animate={{ rotate: 360 }}
      transition={{
        duration: 8,
        repeat: Infinity,
        ease: "linear",
      }}
    >
      <motion.div
        className="absolute w-3 h-3 bg-primary rounded-full"
        style={{ top: 0, left: "calc(50% - 6px)" }}
      />
      <motion.div className="absolute w-full h-full rounded-full border-2 border-primary/30" />
    </motion.div>
  );
};
