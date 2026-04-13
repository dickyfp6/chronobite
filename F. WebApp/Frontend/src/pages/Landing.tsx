import { useState } from 'react';
import { ChevronLeft, ChevronRight, Heart, Activity, Droplet, TrendingDown, Shield, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useI18n } from '../contexts/I18nContext';

const slides = [
  { id: 'intro', icon: Heart },
  { id: 'dm2', icon: Droplet },
  { id: 'hypertension', icon: Activity },
  { id: 'cvd', icon: Heart },
  { id: 'cholesterol', icon: TrendingDown },
  { id: 'ckd', icon: Shield },
];

export function Landing({ onStart }: { onStart: () => void }) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const { t } = useI18n();

  const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % slides.length);
  const prevSlide = () => setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);

  const slideContent = t.landing.slides[slides[currentSlide].id as keyof typeof t.landing.slides];
  const Icon = slides[currentSlide].icon;

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex flex-col">
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8 sm:mb-12"
          >
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4 px-4">
              {t.landing.title}
            </h1>
            <p className="text-base sm:text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto px-4">
              {t.landing.subtitle}
            </p>
          </motion.div>

          <div className="relative overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentSlide}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.3 }}
                className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm rounded-2xl p-6 sm:p-8 md:p-12 border-2 border-emerald-200 dark:border-emerald-600 shadow-xl min-h-[280px] sm:min-h-[320px] flex flex-col items-center justify-center"
              >
                <div className="mb-4 sm:mb-6 p-4 sm:p-6 bg-gradient-to-br from-emerald-400 to-teal-500 dark:from-emerald-500 dark:to-teal-600 rounded-full shadow-lg">
                  <Icon className="w-12 h-12 sm:w-16 sm:h-16 text-white" />
                </div>
                <h2 className="text-xl sm:text-2xl md:text-3xl font-bold mb-3 sm:mb-4 text-center text-gray-900 dark:text-white px-4">
                  {slideContent.title}
                </h2>
                <p className="text-sm sm:text-base text-gray-600 dark:text-gray-300 text-center max-w-2xl leading-relaxed px-4">
                  {slideContent.content}
                </p>
              </motion.div>
            </AnimatePresence>

            <button
              onClick={prevSlide}
              className="absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 p-2 sm:p-3 bg-white dark:bg-slate-700 border-2 border-emerald-200 dark:border-emerald-600 rounded-full hover:bg-gradient-to-br hover:from-emerald-500 hover:to-teal-500 hover:text-white transition-all shadow-lg z-10"
            >
              <ChevronLeft className="w-5 h-5 sm:w-6 sm:h-6" />
            </button>

            <button
              onClick={nextSlide}
              className="absolute right-3 sm:right-4 top-1/2 -translate-y-1/2 p-2 sm:p-3 bg-white dark:bg-slate-700 border-2 border-emerald-200 dark:border-emerald-600 rounded-full hover:bg-gradient-to-br hover:from-emerald-500 hover:to-teal-500 hover:text-white transition-all shadow-lg z-10"
            >
              <ChevronRight className="w-5 h-5 sm:w-6 sm:h-6" />
            </button>
          </div>

          <div className="flex justify-center gap-2 mt-8">
            {slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`h-2 rounded-full transition-all ${
                  index === currentSlide ? 'w-8 bg-gradient-to-r from-emerald-500 to-teal-500' : 'w-2 bg-gray-300 dark:bg-gray-600'
                }`}
              />
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-center mt-8 sm:mt-12 mb-4"
          >
            <button
              onClick={onStart}
              className="px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-medium hover:from-emerald-600 hover:to-teal-600 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 hover:scale-105"
            >
              {t.landing.cta}
            </button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
