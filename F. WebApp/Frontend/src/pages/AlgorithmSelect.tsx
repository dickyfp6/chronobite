import { Zap, Network } from 'lucide-react';
import { motion } from 'motion/react';
import { t } from '../utils/translations';
import { IconCard } from '../components/figma/IconCard';

interface AlgorithmSelectProps {
 selected?: 'greedy' | 'genetic';
 onSelect: (algorithm: 'greedy' | 'genetic') => void;
 onContinue: () => void;
}

export function AlgorithmSelect({ selected, onSelect, onContinue }: AlgorithmSelectProps) {
 return (
 <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-background via-background to-secondary/30 flex items-center justify-center px-4 py-8">
 <motion.div
 initial={{ opacity: 0, y: 20 }}
 animate={{ opacity: 1, y: 0 }}
 className="w-full max-w-3xl"
 >
 <div className="text-center mb-12">
 <h1 className="text-3xl sm:text-4xl font-bold mb-3 text-gray-900 tracking-tight">{t.algorithm.title}</h1>
 <p className="text-gray-600 font-normal">{t.algorithm.subtitle}</p>
 </div>

 <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
 <IconCard
 icon={Zap}
 title={t.algorithm.greedy.title}
 description={t.algorithm.greedy.description}
 selected={selected === 'greedy'}
 onClick={() => onSelect('greedy')}
 onDoubleClick={() => {
  onSelect('greedy');
  onContinue();
 }}
 />
 <IconCard
 icon={Network}
 title={t.algorithm.genetic.title}
 description={t.algorithm.genetic.description}
 selected={selected === 'genetic'}
 onClick={() => onSelect('genetic')}
 onDoubleClick={() => {
  onSelect('genetic');
  onContinue();
 }}
 />
 </div>

 {selected && (
 <motion.div
 initial={{ opacity: 0, y: 10 }}
 animate={{ opacity: 1, y: 0 }}
 className="text-center"
 >
 <button
 onClick={onContinue}
 className="px-8 py-3.5 bg-primary text-primary-foreground rounded-xl font-semibold hover:bg-primary/95 transition-all shadow-md hover:shadow-lg hover:shadow-primary/10 transform hover:-translate-y-0.5 cursor-pointer animate-fade-in"
 >
 {t.algorithm.continue}
 </button>
 </motion.div>
 )}
 </motion.div>
 </div>
 );
}
