import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Heart, Activity, Droplet, TrendingDown, Shield } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { t } from '../utils/translations';

const slides = [
 {
 id: 'intro',
 badge: 'CLINICALLY VALIDATED NUTRITION',
 imageUrl: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80', // Vibrant avocado & egg bowl
 icon: Heart,
 topWidget: {
 title: 'REAL-TIME BIOMETRICS',
 value: 'Stable Glucose',
 icon: Heart
 },
 bottomWidget: {
 title: 'DAILY VITAMIN SCORE',
 value: '94%',
 progress: 94
 }
 },
 {
 id: 'dm2',
 badge: 'DIABETES MELLITUS MANAGEMENT',
 imageUrl: 'https://images.unsplash.com/photo-1493770348161-369560ae357d?auto=format&fit=crop&w=600&q=80', // Oatmeal with fresh berries (Low GI)
 icon: Droplet,
 topWidget: {
 title: 'GLUCOSE LEVEL',
 value: '98 mg/dL (Stable)',
 icon: Droplet
 },
 bottomWidget: {
 title: 'CARBOHYDRATE LIMIT',
 value: '120g / 150g',
 progress: 80
 }
 },
 {
 id: 'hypertension',
 badge: 'HYPERTENSION PROTOCOL',
 imageUrl: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=600&q=80', // Mediterranean salad (Low sodium)
 icon: Activity,
 topWidget: {
 title: 'BLOOD PRESSURE',
 value: '120/80 mmHg',
 icon: Activity
 },
 bottomWidget: {
 title: 'SODIUM INTAKE',
 value: '1,500mg / 2,300mg',
 progress: 65
 }
 },
 {
 id: 'cvd',
 badge: 'CARDIOVASCULAR HEALTH',
 imageUrl: 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=600&q=80', // Grilled salmon (Omega-3)
 icon: Heart,
 topWidget: {
 title: 'CHOLESTEROL STATUS',
 value: 'Normal Range',
 icon: Heart
 },
 bottomWidget: {
 title: 'OMEGA-3 FULFILLED',
 value: '100%',
 progress: 100
 }
 },
 {
 id: 'cholesterol',
 badge: 'CHOLESTEROL MANAGEMENT',
 imageUrl: 'https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?auto=format&fit=crop&w=600&q=80', // Chia pudding / oats (Soluble fiber)
 icon: TrendingDown,
 topWidget: {
 title: 'LDL STATUS',
 value: 'Optimal Level',
 icon: TrendingDown
 },
 bottomWidget: {
 title: 'SOLUBLE FIBER',
 value: '22g / 25g',
 progress: 88
 }
 },
 {
 id: 'ckd',
 badge: 'CHRONIC KIDNEY SUPPORT',
 imageUrl: 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=600&q=80', // Healthy plate, safe for CKD
 icon: Shield,
 topWidget: {
 title: 'FILTRATION RATE',
 value: 'Balanced GFR',
 icon: Shield
 },
 bottomWidget: {
 title: 'PROTEIN INTAKE',
 value: '55g / 60g',
 progress: 91
 }
 }
];

export function Landing({ onStart }: { onStart: () => void }) {
  const [currentSlide, setCurrentSlide] = useState(0);

  const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % slides.length);
  const prevSlide = () => setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);

  // Touch gesture states for mobile swipe support
  const [touchStartX, setTouchStartX] = useState<number | null>(null);
  const [touchEndX, setTouchEndX] = useState<number | null>(null);
  const [touchStartY, setTouchStartY] = useState<number | null>(null);
  const [touchEndY, setTouchEndY] = useState<number | null>(null);
  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEndX(null);
    setTouchEndY(null);
    setTouchStartX(e.targetTouches[0].clientX);
    setTouchStartY(e.targetTouches[0].clientY);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEndX(e.targetTouches[0].clientX);
    setTouchEndY(e.targetTouches[0].clientY);
  };

  const onTouchEnd = () => {
    if (!touchStartX || !touchEndX || !touchStartY || !touchEndY) return;
    const distanceX = touchStartX - touchEndX;
    const distanceY = touchStartY - touchEndY;
    const isHorizontalSwipe = Math.abs(distanceX) > Math.abs(distanceY);
    const isLeftSwipe = distanceX > minSwipeDistance;
    const isRightSwipe = distanceX < -minSwipeDistance;

    if (isHorizontalSwipe) {
      if (isLeftSwipe) {
        nextSlide();
      } else if (isRightSwipe) {
        prevSlide();
      }
    }
  };

  // Auto slide per 5 detik
  useEffect(() => {
    const timer = setInterval(() => {
      nextSlide();
    }, 5000);
    return () => clearInterval(timer);
  }, [currentSlide]);

  const slide = slides[currentSlide];
  const slideContent = t.landing.slides[slide.id as keyof typeof t.landing.slides];
  const WidgetIcon = slide.topWidget.icon;

  return (
    <div 
      className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-background via-background to-secondary/30 flex flex-col justify-center"
    >
      <div className="flex-1 flex items-center justify-center py-6 md:py-12 px-4 sm:px-6 lg:px-8">
        <div 
          className="w-full max-w-6xl relative"
          onTouchStart={onTouchStart}
          onTouchMove={onTouchMove}
          onTouchEnd={onTouchEnd}
        >
 <div className="grid grid-cols-1 md:grid-cols-12 gap-8 lg:gap-16 items-stretch">
 
 {/* Left Column: Text (Sliding) and CTA (Static) */}
 <div className="col-span-1 md:col-span-7 flex flex-col text-left justify-between md:min-h-[420px]">
 
 {/* Dynamic Text Section */}
 <div className="flex-1 flex flex-col justify-center">
 <AnimatePresence mode="wait">
 <motion.div
 key={currentSlide}
 initial={{ opacity: 0, y: 10 }}
 animate={{ opacity: 1, y: 0 }}
 exit={{ opacity: 0, y: -10 }}
 transition={{ duration: 0.2, ease: 'easeOut' }}
 className="space-y-4"
 >
 <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-primary/10 text-primary rounded-full text-xs font-bold uppercase tracking-wider font-sans border border-primary/20">
 {slide.badge}
 </span>
 
 <h1 className="text-2xl sm:text-4xl lg:text-5xl font-bold text-gray-900 leading-tight font-serif tracking-tight md:min-h-[130px] flex items-center">
 {slideContent.title}
 </h1>
 
 <p className="text-base sm:text-lg text-gray-600 font-sans leading-relaxed max-w-xl md:min-h-[80px]">
 {slideContent.content}
 </p>
 </motion.div>
 </AnimatePresence>
 </div>

 {/* Desktop CTA Section (Button only - no dots, hidden on mobile) */}
 <div className="hidden md:block pt-6">
 <button
 onClick={onStart}
 className="px-8 py-4 bg-primary text-primary-foreground rounded-2xl font-bold text-lg hover:bg-primary/95 transition-all shadow-md hover:shadow-lg hover:shadow-primary/10 cursor-pointer transform hover:-translate-y-0.5"
 >
 {t.landing.cta}
 </button>
 </div>
 </div>

 {/* Right Column: Image and overlapping Widgets (Dynamic Sliding) */}
 <div className="col-span-1 md:col-span-5 relative mt-6 md:mt-0 flex items-center justify-center">
 <div className="relative w-full max-w-[420px] aspect-square md:aspect-[4/5]">
 <AnimatePresence mode="wait">
 <motion.div
 key={currentSlide}
 initial={{ opacity: 0, scale: 0.97 }}
 animate={{ opacity: 1, scale: 1 }}
 exit={{ opacity: 0, scale: 0.97 }}
 transition={{ duration: 0.2, ease: 'easeOut' }}
 className="w-full h-full relative"
 >
 <div className="w-full h-full rounded-[32px] overflow-hidden shadow-2xl relative">
 <img
 src={slide.imageUrl}
 alt={slideContent.title}
 className="w-full h-full object-cover"
 />
 <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent pointer-events-none" />
 
 {/* Bottom Vitamin Score widget overlay */}
 <div className="absolute bottom-4 left-4 right-4 bg-white/90 backdrop-blur-md p-4 rounded-2xl border border-border/80 shadow-lg">
 <div className="flex justify-between items-center mb-2">
 <span className="text-[10px] font-bold text-gray-500 tracking-wider uppercase">
 {slide.bottomWidget.title}
 </span>
 <span className="text-xs font-bold text-primary ">
 {slide.bottomWidget.value}
 </span>
 </div>
 <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
 <div
 className="bg-primary h-full rounded-full transition-all duration-500"
 style={{ width: `${slide.bottomWidget.progress}%` }}
 />
 </div>
 </div>
 </div>

 {/* Top Right Biometrics floating card */}
 <div className="absolute -top-6 -right-2 bg-white/95 backdrop-blur-md py-3 px-4 rounded-2xl border border-border/80 shadow-xl flex items-center gap-3">
 <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
 <WidgetIcon className="w-4 h-4" />
 </div>
 <div className="text-left font-sans">
 <span className="block text-[8px] font-bold text-gray-500 tracking-wider uppercase leading-none mb-0.5">
 {slide.topWidget.title}
 </span>
 <span className="block text-xs font-extrabold text-gray-900 ">
 {slide.topWidget.value}
 </span>
 </div>
 </div>
 </motion.div>
 </AnimatePresence>
 </div>
 </div>
 
 </div>

 {/* Dots Pagination & Mobile CTA Container */}
 <div className="mt-8 md:mt-10 flex flex-col items-center gap-6">
 {/* Dots Pagination (Centered for both Desktop & Mobile) */}
 <div className="flex gap-2">
 {slides.map((_, index) => (
 <button
 key={index}
 onClick={() => setCurrentSlide(index)}
 className={`h-2 rounded-full transition-all cursor-pointer ${
 index === currentSlide ? 'w-8 bg-primary animate-pulse' : 'w-2 bg-border hover:bg-primary/40'
 }`}
 aria-label={`Go to slide ${index + 1}`}
 />
 ))}
 </div>

 {/* Mobile CTA Button (Hidden on Desktop, full-width at the bottom of mobile) */}
 <div className="w-full md:hidden px-4">
 <button
 onClick={onStart}
 className="w-full py-4 bg-primary text-primary-foreground rounded-2xl font-bold text-base hover:bg-primary/95 transition-all shadow-md hover:shadow-lg hover:shadow-primary/10 cursor-pointer text-center block"
 >
 {t.landing.cta}
 </button>
 </div>
 </div>

 {/* Elegant navigation arrows outside/sides */}
 <button
 onClick={prevSlide}
 className="absolute left-[-20px] md:left-[-60px] top-1/2 -translate-y-1/2 p-2.5 bg-white/90 border border-border/85 rounded-full hover:bg-primary hover:text-white transition-all shadow-md backdrop-blur-sm cursor-pointer z-20 hidden md:block"
 aria-label="Previous slide"
 >
 <ChevronLeft className="w-5 h-5" />
 </button>

 <button
 onClick={nextSlide}
 className="absolute right-[-20px] md:right-[-60px] top-1/2 -translate-y-1/2 p-2.5 bg-white/90 border border-border/85 rounded-full hover:bg-primary hover:text-white transition-all shadow-md backdrop-blur-sm cursor-pointer z-20 hidden md:block"
 aria-label="Next slide"
 >
 <ChevronRight className="w-5 h-5" />
 </button>
 </div>
 </div>
 </div>
 );
}
