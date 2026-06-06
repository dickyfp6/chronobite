import { motion } from 'motion/react';

interface IconCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description?: string;
  selected?: boolean;
  disabled?: boolean;
  onClick?: () => void;
}

export function IconCard({ icon: Icon, title, description, selected, disabled, onClick }: IconCardProps) {
  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.01 }}
      whileTap={{ scale: disabled ? 1 : 0.99 }}
      onClick={onClick}
      disabled={disabled}
      className={`p-6 rounded-2xl border transition-all text-left w-full cursor-pointer ${
        selected
          ? 'border-primary dark:border-primary bg-emerald-500/10 dark:bg-emerald-500/15 shadow-md ring-2 ring-primary/20'
          : disabled
          ? 'border-border/40 dark:border-slate-800/50 bg-slate-50/50 dark:bg-slate-800/20 opacity-35 cursor-not-allowed'
          : 'border-border/80 dark:border-slate-700/60 bg-white/40 dark:bg-slate-800/20 hover:border-primary dark:hover:border-primary/80 hover:shadow-sm hover:bg-white/95 dark:hover:bg-slate-800/80'
      }`}
    >
      <div className="flex flex-col items-center text-center gap-3">
        <div className={`p-4 rounded-full transition-all ${selected ? 'bg-primary text-primary-foreground shadow-sm' : 'bg-secondary dark:bg-slate-800 text-primary dark:text-emerald-400'}`}>
          <Icon className="w-8 h-8" />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-white text-base tracking-tight">{title}</h3>
          {description && (
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 font-normal leading-normal">{description}</p>
          )}
        </div>
      </div>
    </motion.button>
  );
}
