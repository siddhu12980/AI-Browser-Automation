"use client";
import { motion, useScroll, useTransform } from "framer-motion";
import { Button } from "./ui/button";
import { ArrowRight } from "lucide-react";
import { CircleIcon, PulseIcon } from "./AnimatedIcons";

export default function CTASection() {
  const { scrollYProgress } = useScroll();
  const scale = useTransform(scrollYProgress, [0.5, 1], [0.8, 1]);
  const opacity = useTransform(scrollYProgress, [0.5, 0.8], [0, 1]);

  return (
    <section className="container px-4 py-24 mx-auto">
      <motion.div
        style={{ scale, opacity }}
        className="bg-secondary/30 rounded-3xl p-12 text-center space-y-6 relative"
      >
        <motion.div
          animate={{
            y: [0, -10, 0],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute -top-6 -right-6"
        >
          <CircleIcon />
        </motion.div>
        <motion.div
          animate={{
            y: [0, 10, 0],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1,
          }}
          className="absolute -bottom-6 -left-6"
        >
          <PulseIcon />
        </motion.div>
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-4xl font-bold"
        >
          Ready to Transform Your Workflow?
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-xl text-muted-foreground max-w-2xl mx-auto"
        >
          Join thousands of users who have already revolutionized their desktop
          experience with our AI assistant.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <Button size="lg" className="gap-2 group">
            Download Now{" "}
            <motion.span
              animate={{ x: [0, 5, 0] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              <ArrowRight className="w-4 h-4" />
            </motion.span>
          </Button>
        </motion.div>
      </motion.div>
    </section>
  );
}
