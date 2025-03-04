"use client";
import HeroSection from "@/components/HeroSection";
import FeaturesSection from "@/components/FeaturesSection";
import CTASection from "@/components/CTASection";
import SmoothScroll from "@/components/SmoothScroll";
import AssistantSection from "@/components/AssistantSection";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <SmoothScroll />
      <main className="min-h-screen bg-gradient-to-r from-light-blue-100 via-pink-100 to-light-blue-200 overflow-hidden">
        <HeroSection />
        <AssistantSection />
        <FeaturesSection />
        <CTASection />
      </main>
      <Footer />
    </>
  );
}
