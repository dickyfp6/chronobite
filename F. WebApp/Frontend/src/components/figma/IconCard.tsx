import { motion } from 'motion/react';
import { Check } from 'lucide-react';

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
  backgroundImage?: string;
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
  iconBgUnselectedClass = 'bg-primary/80',
  backgroundImage
}: IconCardProps) {
  // If has background image — render full-image card like cuisine cards
  if (backgroundImage) {
    return (
      <motion.button
        whileHover={{ scale: disabled ? 1 : 1.02, y: disabled ? 0 : -3 }}
        whileTap={{ scale: disabled ? 1 : 0.98 }}
        onClick={onClick}
        onDoubleClick={onDoubleClick}
        disabled={disabled}
        className={`group/card relative rounded-2xl overflow-hidden cursor-pointer transition-all duration-300 w-full text-left min-h-[96px] sm:min-h-[108px] flex ${
          selected
            ? 'ring-2 ring-primary shadow-[0_0_18px_3px_rgba(45,90,39,0.45)]'
            : disabled
            ? 'opacity-35 cursor-not-allowed ring-1 ring-white/10'
            : 'ring-1 ring-black/10 hover:ring-2 hover:ring-primary/40 hover:shadow-lg'
        } ${className}`}
      >
        {/* Background image — grayscale when unselected, full color when selected or hovered */}
        <div
          className={`absolute inset-0 bg-cover bg-center transition-all duration-500 ${
            selected
              ? 'grayscale-0 scale-[1.06] brightness-80 blur-[2px]'
              : 'grayscale brightness-70 blur-[2px] group-hover/card:grayscale-0 group-hover/card:brightness-85 group-hover/card:scale-[1.03]'
          }`}
          style={{ backgroundImage: `url(${backgroundImage})` }}
        />

        {/* Gradient scrim — heavier at center/bottom for readability */}
        <div className={`absolute inset-0 transition-all duration-300 ${
          selected
            ? 'bg-gradient-to-br from-black/20 via-black/30 to-black/50'
            : 'bg-gradient-to-br from-black/30 via-black/40 to-black/60 group-hover/card:from-black/20 group-hover/card:via-black/30 group-hover/card:to-black/50'
        }`} />

        {/* Selected checkmark */}
        {selected && (
          <div className="absolute top-2.5 right-2.5 z-20 w-6 h-6 rounded-full bg-primary shadow-lg shadow-primary/40 flex items-center justify-center">
            <Check className="w-3.5 h-3.5 text-white" strokeWidth={3} />
          </div>
        )}

        {/* Center content */}
        <div className="relative z-10 flex flex-col items-center justify-center gap-2 w-full px-4 py-4">
          {/* Icon */}
          <div className={`p-2.5 rounded-xl transition-all duration-300 ${
            selected
              ? 'bg-primary shadow-lg shadow-primary/30 ring-2 ring-white/30'
              : 'bg-white/15 backdrop-blur-sm ring-1 ring-white/20 group-hover/card:bg-white/25'
          }`}>
            <Icon className={`w-5 h-5 transition-all duration-300 ${selected ? 'text-white' : 'text-white/90'}`} />
          </div>

          {/* Glassy text pill */}
          <div className={`w-full backdrop-blur-md rounded-xl px-3 py-1.5 text-center transition-all duration-300 ${
            selected
              ? 'bg-primary border border-primary shadow-inner'
              : 'bg-black/45 border border-white/10 group-hover/card:bg-black/35 group-hover/card:border-white/20'
          }`}>
            <h3 className={`font-bold text-sm tracking-widest leading-tight uppercase transition-colors duration-300 ${
              selected ? 'text-white' : 'text-white/85 group-hover/card:text-white'
            }`}>{title}</h3>
            {description && (
              <p className="text-[10px] text-white/55 mt-0.5 font-normal leading-tight group-hover/card:text-white/70 transition-colors duration-300">{description}</p>
            )}
          </div>
        </div>
      </motion.button>
    );
  }

  // Default: no background image — plain card style
  const bgSelected = `${iconBgSelectedClass} text-white`;
  const bgUnselected = `${iconBgUnselectedClass} text-slate-100/90`;

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.015, y: disabled ? 0 : -2 }}
      whileTap={{ scale: disabled ? 1 : 0.985 }}
      onClick={onClick}
      onDoubleClick={onDoubleClick}
      disabled={disabled}
      className={`group/plain p-4 sm:p-5 rounded-2xl border transition-all text-left w-full cursor-pointer relative overflow-hidden ${
        selected
          ? 'border-primary bg-emerald-500/[0.08] shadow-md shadow-emerald-500/5 ring-1 ring-primary/30'
          : disabled
          ? 'border-border/45 bg-slate-50/50 opacity-35 cursor-not-allowed'
          : 'border-border/80 bg-white/40 hover:border-primary/80 hover:shadow-md hover:bg-white/95 hover:shadow-primary/5'
      } ${className}`}
    >
      <div className="flex items-center gap-4 relative z-10 w-full">
        <div className={`p-3 rounded-xl shrink-0 transition-all duration-300 ${selected ? `${bgSelected} shadow-md scale-105 ring-2 ring-primary/20` : bgUnselected}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold text-sm sm:text-base tracking-tight leading-tight transition-colors duration-200 ${selected ? 'text-primary' : 'text-gray-900'}`}>{title}</h3>
          {description && (
            <p className="text-[11px] text-gray-500 mt-1 font-normal leading-normal">{description}</p>
          )}
        </div>
        {selected && (
          <div className="shrink-0 w-5 h-5 rounded-full bg-primary flex items-center justify-center shadow-sm">
            <Check className="w-3 h-3 text-white" strokeWidth={3} />
          </div>
        )}
      </div>
    </motion.button>
  );
}
