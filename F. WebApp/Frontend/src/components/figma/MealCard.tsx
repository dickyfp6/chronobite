import { RefreshCw } from 'lucide-react';
import { motion } from 'motion/react';
import { useState } from 'react';

interface MealOption {
  id: string;
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

interface MealCardProps {
  category: string;
  options: MealOption[];
  selected?: string;
  onSelect?: (id: string) => void;
  onRefresh?: () => void;
  optional?: boolean;
}

export function MealCard({ category, options, selected, onSelect, onRefresh, optional }: MealCardProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    onRefresh?.();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-emerald-900">
          {category} {optional && <span className="text-xs text-emerald-600">(Optional)</span>}
        </h4>
        <button
          onClick={handleRefresh}
          className="p-2 hover:bg-emerald-100 rounded-lg transition-all text-emerald-600 hover:text-emerald-700"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="grid grid-cols-1 gap-2">
        {options.map((option) => (
          <motion.button
            key={option.id}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={() => onSelect?.(option.id)}
            className={`p-3 rounded-lg border-2 text-left transition-all ${
              selected === option.id
                ? 'border-emerald-400 bg-gradient-to-br from-emerald-50 to-teal-50 shadow-md'
                : 'border-emerald-200 hover:border-emerald-400 hover:shadow-sm'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="font-medium text-sm text-emerald-900">{option.name}</p>
                <p className="text-xs text-emerald-600 mt-1">
                  {option.calories} cal • P: {option.protein}g • C: {option.carbs}g • F: {option.fat}g
                </p>
              </div>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
