import { LucideIcon } from 'lucide-react';
import { motion } from 'motion/react';

interface IconCardProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  selected?: boolean;
  disabled?: boolean;
  onClick?: () => void;
}

export function IconCard({ icon: Icon, title, description, selected, disabled, onClick }: IconCardProps) {
  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      onClick={onClick}
      disabled={disabled}
      className={`p-6 rounded-xl border-2 transition-all text-left w-full ${
        selected
          ? 'border-emerald-500 dark:border-emerald-400 bg-gradient-to-br from-emerald-100 to-teal-100 dark:from-emerald-900/50 dark:to-teal-900/50 shadow-lg ring-2 ring-emerald-400/50 dark:ring-emerald-400/30'
          : disabled
          ? 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 opacity-50 cursor-not-allowed'
          : 'border-emerald-200 dark:border-emerald-700 hover:border-emerald-400 dark:hover:border-emerald-500 hover:shadow-md hover:bg-emerald-50/50 dark:hover:bg-emerald-900/20'
      }`}
    >
      <div className="flex flex-col items-center text-center gap-3">
        <div className={`p-4 rounded-full ${selected ? 'bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-lg' : 'bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300'}`}>
          <Icon className="w-8 h-8" />
        </div>
        <div>
          <h3 className="font-medium text-gray-900 dark:text-white">{title}</h3>
          {description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{description}</p>
          )}
        </div>
      </div>
    </motion.button>
  );
}
