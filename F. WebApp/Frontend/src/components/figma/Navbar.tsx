import { useState } from 'react';
import lightLogo from '../../assets/ChronoBite.png';
import { t } from '../../utils/translations';
import { Download, Calculator } from 'lucide-react';
import { BmiCalculatorModal } from './BmiCalculatorModal';

interface NavbarProps {
 onHomeClick: () => void;
 currentPage: string;
 onDownloadPDF?: (() => void) | null;
}

export function Navbar({ onHomeClick, currentPage, onDownloadPDF }: NavbarProps) {
 const [isBmiOpen, setIsBmiOpen] = useState(false);
 let title = '';
 if (currentPage === 'input') {
 title = t.input.title;
 } else if (currentPage === 'profile') {
 title = 'Your Profile Summary';
 } else if (currentPage === 'results') {
 title = t.results.title;
 } else if (currentPage === 'report') {
 title = t.report.title;
 }
 
 return (
 <>
 <nav className="fixed top-0 left-0 right-0 z-50 bg-white/70 backdrop-blur-md border-b border-border/70 shadow-sm">
 <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between relative">
 <button
 onClick={onHomeClick}
 className="cursor-pointer transition-all duration-300 hover:drop-shadow-[0_0_12px_rgba(45,90,39,0.4)]"
 >
 <img
 src={lightLogo}
 alt="ChronoBite"
 className="h-12"
 />
 </button>
 
 {title && (
 <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 font-bold text-xl text-gray-900 font-serif hidden sm:block">
 {title}
 </div>
 )}

 <div className="flex items-center gap-3 sm:gap-4 z-10">
  {currentPage === 'report' && onDownloadPDF && (
  <button
    onClick={onDownloadPDF}
    className="w-10 h-10 sm:w-auto sm:px-4 sm:py-2.5 bg-primary text-primary-foreground rounded-full sm:rounded-xl font-semibold hover:bg-primary/95 transition-all flex items-center justify-center sm:justify-start gap-2 shadow-md hover:shadow-lg hover:shadow-primary/10 cursor-pointer shrink-0 text-xs sm:text-sm"
    title={t.report.download}
  >
    <Download className="w-5 h-5 sm:w-4 sm:h-4" />
    <span className="hidden sm:inline">{t.report.download}</span>
  </button>
  )}
      <button
        onClick={() => setIsBmiOpen(true)}
        className="w-10 h-10 flex items-center justify-center bg-white border border-gray-100/80 rounded-full text-primary hover:text-primary/90 shadow-md hover:shadow-lg transition-all duration-300 cursor-pointer transform hover:-translate-y-0.5 active:translate-y-0"
        title="BMI Calculator"
      >
        <Calculator className="w-5 h-5" />
      </button>
 </div>
 </div>
 </nav>

 <BmiCalculatorModal isOpen={isBmiOpen} onClose={() => setIsBmiOpen(false)} />
 </>
 );
}

