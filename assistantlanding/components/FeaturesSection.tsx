"use client";
import { motion } from "framer-motion";
import { Bot, Command } from "lucide-react";
import { WaveformIcon, PulseIcon, CircleIcon } from "./AnimatedIcons";

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.8,
    },
  },
};

export default function FeaturesSection() {
  return (
    <section className="container px-4 py-24 mx-auto">
      <motion.div
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="grid grid-cols-1 md:grid-cols-3 gap-8"
      >
        <FeatureCard
          icon={<WaveformIcon />}
          animatedIcon={<PulseIcon />}
          title="Voice Commands"
          description="Control your computer naturally with voice commands and conversations."
        />
        <FeatureCard
          icon={<Bot className="w-8 h-8" />}
          animatedIcon={<CircleIcon />}
          title="Smart Automation"
          description="Automate repetitive tasks and boost your productivity with AI-powered workflows."
        />
        <FeatureCard
          icon={<Command className="w-8 h-8" />}
          animatedIcon={<WaveformIcon />}
          title="Quick Actions"
          description="Access any feature or command instantly with natural language shortcuts."
        />
      </motion.div>
    </section>
  );
}

function FeatureCard({
  icon,
  animatedIcon,
  title,
  description,
}: {
  icon: React.ReactNode;
  animatedIcon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <motion.div
      variants={itemVariants}
      whileHover={{ scale: 1.05 }}
      className="p-6 rounded-2xl bg-card border shadow-sm hover:shadow-lg transition-shadow relative overflow-hidden"
    >
      <div className="bg-primary/20 w-fit p-3 rounded-xl mb-4">{icon}</div>
      <motion.div
        className="absolute top-2 right-2 opacity-0 transition-opacity duration-300"
        whileHover={{ opacity: 1 }}
      >
        {animatedIcon}
      </motion.div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </motion.div>
  );
}
