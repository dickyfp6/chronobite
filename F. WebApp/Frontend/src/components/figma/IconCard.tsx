import { motion } from 'motion/react';

interface IconCardProps {
 icon: React.ComponentType<{ className?: string }>;
 title: string;
 description?: string;
 selected?: boolean;
 disabled?: boolean;
 onClick?: () => void;
 onDoubleClick?: () => void;
 className?: string;
 iconBgSelectedClass?: string;
 iconBgUnselectedClass?: string;
}

export function IconCard({
  icon: Icon,
  title,
  description,
  selected,
  disabled,
  onClick,
  onDoubleClick,
  className = '',
  iconBgSelectedClass = 'bg-primary',
  iconBgUnselectedClass = 'bg-primary/80'
}: IconCardProps) {
  const bgSelected = `${iconBgSelectedClass} text-white`;
  const bgUnselected = `${iconBgUnselectedClass} text-slate-100/90`;

 return (
 <motion.button
 whileHover={{ scale: disabled ? 1 : 1.015, y: disabled ? 0 : -2 }}
 whileTap={{ scale: disabled ? 1 : 0.985 }}
 onClick={onClick}
 onDoubleClick={onDoubleClick}
 disabled={disabled}
 className={`p-4 sm:p-5 rounded-2xl border transition-all text-left w-full cursor-pointer relative overflow-hidden ${
 selected
 ? 'border-primary bg-emerald-500/[0.08] shadow-md shadow-emerald-500/5 ring-1 ring-primary/30'
 : disabled
 ? 'border-border/45 bg-slate-50/50 opacity-35 cursor-not-allowed'
 : 'border-border/80 bg-white/40 hover:border-primary/80 :border-primary/60 hover:shadow-md hover:bg-white/95 :bg-slate-800/80 hover:shadow-primary/5'
 } ${className}`}
 >
 <div className="flex items-center gap-4">
  <div className={`p-3 rounded-xl shrink-0 transition-all duration-300 ${selected ? `${bgSelected} shadow-md scale-105 ring-2 ring-white/25` : bgUnselected}`}>
 <Icon className="w-6 h-6" />
 </div>
 <div className="flex-1 min-w-0">
 <h3 className="font-semibold text-gray-900 text-sm sm:text-base tracking-tight leading-tight">{title}</h3>
 {description && (
 <p className="text-xs text-gray-500 mt-1 font-normal leading-normal">{description}</p>
 )}
 </div>
 </div>
 </motion.button>
 );
}
