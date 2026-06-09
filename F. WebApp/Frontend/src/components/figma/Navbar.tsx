import lightLogo from '../../assets/ChronoBite.png';
import { t } from '../../utils/translations';
import { Download } from 'lucide-react';

interface NavbarProps {
 onHomeClick: () => void;
 currentPage: string;
 onDownloadPDF?: (() => void) | null;
}

export function Navbar({ onHomeClick, currentPage, onDownloadPDF }: NavbarProps) {
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

 <div className="flex items-center gap-4 z-10">
 {currentPage === 'report' && onDownloadPDF && (
 <button
 onClick={onDownloadPDF}
 className="px-4 py-2 bg-primary text-primary-foreground rounded-xl font-semibold hover:bg-primary/95 transition-all flex items-center gap-2 shadow-md hover:shadow-lg hover:shadow-primary/10 cursor-pointer text-xs sm:text-sm"
 >
 <Download className="w-3.5 h-3.5" />
 <span>{t.report.download}</span>
 </button>
 )}
 </div>
 </div>
 </nav>
 );
}
