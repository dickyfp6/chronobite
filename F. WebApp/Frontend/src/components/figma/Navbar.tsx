import lightLogo from '../../assets/light-horizontal.png';

interface NavbarProps {
  onHomeClick: () => void;
}

export function Navbar({ onHomeClick }: NavbarProps) {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/70 backdrop-blur-md border-b border-border/70 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <button
          onClick={onHomeClick}
          className="cursor-pointer transition-all duration-300 hover:drop-shadow-[0_0_12px_rgba(45,90,39,0.4)]"
        >
          <img
            src={lightLogo}
            alt="NutriPlan"
            className="h-12"
          />
        </button>
      </div>
    </nav>
  );
}
