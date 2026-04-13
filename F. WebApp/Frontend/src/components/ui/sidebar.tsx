"use client";

import * as React from "react";
import * as SidebarPrimitive from "@/components/ui/sidebar";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { Menu, X } from "lucide-react";

import { cn } from "./utils";

const SIDEBAR_COOKIE_NAME = "sidebar:state";
const SIDEBAR_COOKIE_MAX_AGE = 60 * 60 * 24 * 7;
const SIDEBAR_WIDTH = "16rem";
const SIDEBAR_WIDTH_MOBILE = "18rem";
const SIDEBAR_WIDTH_ICON = "3rem";
const SIDEBAR_KEYBOARD_SHORTCUT = "b";

type SidebarState = "expanded" | "collapsed";

interface SidebarContext {
  state: SidebarState;
  open: boolean;
  setOpen: (open: boolean) => void;
  openMobile: boolean;
  setOpenMobile: (open: boolean) => void;
  isMobile: boolean;
  toggleSidebar: () => void;
}

const SidebarContext = React.createContext<SidebarContext | undefined>(
  undefined,
);

function useSidebar() {
  const context = React.useContext(SidebarContext);
  if (!context) {
    throw new Error("useSidebar must be used within a SidebarProvider");
  }
  return context;
}

const SidebarProvider = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    defaultOpen?: boolean;
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
  }
>(
  (
    {
      defaultOpen = true,
      open: openProp,
      onOpenChange: setOpenProp,
      className,
      style,
      children,
      ...props
    },
    ref,
  ) => {
    const isMobile = typeof window !== "undefined" && window.innerWidth < 768;
    const [openMobile, setOpenMobile] = React.useState(false);

    const [_open, _setOpen] = React.useState(defaultOpen);
    const open = openProp ?? _open;
    const setOpen = React.useCallback(
      (value: boolean | ((value: boolean) => boolean)) => {
        const openValue = typeof value === "function" ? value(open) : value;
        if (setOpenProp) {
          setOpenProp(openValue);
        } else {
          _setOpen(openValue);
        }

        if (typeof document !== "undefined") {
          document.cookie = `${SIDEBAR_COOKIE_NAME}=${openValue}; path=/; max-age=${SIDEBAR_COOKIE_MAX_AGE}`;
        }
      },
      [open, setOpenProp],
    );

    const toggleSidebar = React.useCallback(() => {
      return isMobile
        ? setOpenMobile((open) => !open)
        : setOpen((open) => !open);
    }, [isMobile, setOpen, setOpenMobile]);

    const state: SidebarState = open ? "expanded" : "collapsed";

    const value: SidebarContext = {
      state,
      open,
      setOpen,
      openMobile,
      setOpenMobile,
      isMobile,
      toggleSidebar,
    };

    return (
      <SidebarContext.Provider value={value}>
        <div
          style={
            {
              "--sidebar-width": SIDEBAR_WIDTH,
              "--sidebar-width-mobile": SIDEBAR_WIDTH_MOBILE,
              "--sidebar-width-icon": SIDEBAR_WIDTH_ICON,
              ...style,
            } as React.CSSProperties
          }
          className={cn(
            "group/sidebar-wrapper flex min-h-svh w-full has-[(footer)]:flex-col",
            className,
          )}
          ref={ref}
          {...props}
        >
          {children}
        </div>
      </SidebarContext.Provider>
    );
  },
);
SidebarProvider.displayName = "SidebarProvider";

const Sidebar = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    side?: "left" | "right";
    variant?: "sidebar" | "floating" | "inset";
    collapsible?: "offcanvas" | "icon" | "none";
  }
>(
  (
    {
      side = "left",
      variant = "sidebar",
      collapsible = "offcanvas",
      className,
      children,
      ...props
    },
    ref,
  ) => {
    const { isMobile, state, openMobile, setOpenMobile } = useSidebar();

    if (collapsible === "none") {
      return (
        <div
          className={cn("flex h-full w-[--sidebar-width] flex-col", className)}
          ref={ref}
          {...props}
        >
          {children}
        </div>
      );
    }

    if (isMobile) {
      return (
        <div
          style={
            {
              "--sidebar-width": "18rem",
            } as React.CSSProperties
          }
          className="group/sidebar relative inline-flex w-0"
        >
          <div
            className={cn(
              "pointer-events-none absolute inset-y-0 left-0 z-10 w-[--sidebar-width] transition-[width,margin] duration-300 ease-in-out lg:pointer-events-auto lg:relative lg:flex lg:w-[--sidebar-width]",
              openMobile ? "pointer-events-auto w-[--sidebar-width]" : "w-0",
            )}
          />
          <Sheet open={openMobile} onOpenChange={setOpenMobile}>
            <SheetContent
              data-sidebar="sidebar"
              data-mobile="true"
              className="w-[--sidebar-width] bg-sidebar p-0 text-sidebar-foreground [&>button]:hidden"
              side={side}
            >
              <div className="flex h-full w-full flex-col">{children}</div>
            </SheetContent>
          </Sheet>
        </div>
      );
    }

    return (
      <div
        ref={ref}
        data-sidebar="sidebar"
        className={cn(
          "group/sidebar relative hidden md:flex h-svh w-[--sidebar-width] flex-col border-r transition-[width,margin] duration-300 ease-in-out",
          state === "collapsed" && "w-[--sidebar-width-icon]",
          variant === "floating" || variant === "inset"
            ? "absolute inset-y-0 z-10 h-svh"
            : "",
          variant === "inset" && "border-0",
          className,
        )}
        {...props}
      >
        {children}
      </div>
    );
  },
);
Sidebar.displayName = "Sidebar";

const SidebarTrigger = React.forwardRef<
  React.ElementRef<typeof SidebarPrimitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof SidebarPrimitive.Trigger>
>(({ className, onClick, ...props }, ref) => {
  const { toggleSidebar } = useSidebar();

  return (
    <button
      ref={ref}
      data-sidebar="trigger"
      onClick={(event) => {
        onClick?.(event);
        toggleSidebar();
      }}
      className={cn("inline-flex items-center justify-center", className)}
      {...props}
    >
      <Menu className="h-4 w-4" />
    </button>
  );
});
SidebarTrigger.displayName = "SidebarTrigger";

const SidebarRail = React.forwardRef<
  HTMLButtonElement,
  React.HTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) => {
  const { toggleSidebar } = useSidebar();

  return (
    <button
      ref={ref}
      data-sidebar="rail"
      aria-label="Toggle Sidebar"
      onClick={toggleSidebar}
      className={cn(
        "absolute inset-y-0 -right-4 hidden w-4 -translate-x-1/2 transition-all ease-linear after:absolute after:inset-y-0 after:left-1/2 after:w-1 after:-translate-x-1/2 hover:after:bg-accent focus-visible:after:bg-accent group-hover/sidebar:after:bg-accent",
        className,
      )}
      {...props}
    />
  );
});
SidebarRail.displayName = "SidebarRail";

const sidebarInsetVariants = cva(
  "relative flex min-h-svh w-full flex-col bg-background peer-data-[state=collapsed]/sidebar-wrapper:peer-data-[variant=inset]/sidebar-wrapper:peer-data-[collapsible=icon]/sidebar-wrapper:ml-[calc(var(--sidebar-width-icon)_-_1px)]",
  {
    variants: {
      variant: {
        default: "peer-data-[variant=floating]/sidebar-wrapper:rounded-lg peer-data-[variant=inset]/sidebar-wrapper:rounded-lg",
        inset:
          "peer-data-[variant=inset]/sidebar-wrapper:border peer-data-[variant=inset]/sidebar-wrapper:rounded-lg",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

interface SidebarInsetProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof sidebarInsetVariants> {}

const SidebarInset = React.forwardRef<
  HTMLDivElement,
  SidebarInsetProps
>(({ variant, className, ...props }, ref) => (
  <main
    ref={ref}
    className={cn(sidebarInsetVariants({ variant }), className)}
    {...props}
  />
));
SidebarInset.displayName = "SidebarInset";

const SidebarContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-sidebar="content"
    className={cn(
      "flex min-h-0 flex-1 flex-col gap-0 overflow-y-auto group-data-[collapsible=icon]/sidebar-wrapper:overflow-hidden",
      className,
    )}
    {...props}
  />
));
SidebarContent.displayName = "SidebarContent";

const SidebarGroup = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-sidebar="group"
    className={cn(
      "relative flex w-full min-w-0 flex-col gap-2 p-2 group-data-[collapsible=icon]/sidebar-wrapper:px-2",
      className,
    )}
    {...props}
  />
));
SidebarGroup.displayName = "SidebarGroup";

const SidebarGroupLabel = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    asChild?: boolean;
  }
>(({ className, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "div";

  return (
    <Comp
      ref={ref}
      data-sidebar="group-label"
      className={cn(
        "px-2 py-1.5 text-xs font-medium text-sidebar-foreground/70 transition-[margin,opa] duration-200 group-hover:text-sidebar-foreground group-data-[collapsible=icon]/sidebar-wrapper:px-2 [&>svg]:pointer-events-none [&>svg]:size-4 [&>svg]:shrink-0",
        className,
      )}
      {...props}
    />
  );
});
SidebarGroupLabel.displayName = "SidebarGroupLabel";

const SidebarGroupAction = React.forwardRef<
  HTMLButtonElement,
  React.HTMLAttributes<HTMLButtonElement> & {
    asChild?: boolean;
  }
>(({ className, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      ref={ref}
      data-sidebar="group-action"
      className={cn(
        "absolute right-3 top-3.5 display:none rounded-md p-1 outline-none ring-sidebar-ring transition-transform hover:bg-sidebar-accent focus-visible:ring-2 group-focus-within/sidebar-group:display:block group-hover/sidebar-group:display:block group-data-[collapsible=icon]/sidebar-wrapper:hidden",
        className,
      )}
      {...props}
    />
  );
});
SidebarGroupAction.displayName = "SidebarGroupAction";

const SidebarGroupContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-sidebar="group-content"
    className={cn("w-full text-sm", className)}
    {...props}
  />
));
SidebarGroupContent.displayName = "SidebarGroupContent";

const SidebarMenu = React.forwardRef<
  HTMLUListElement,
  React.HTMLAttributes<HTMLUListElement>
>(({ className, ...props }, ref) => (
  <ul
    ref={ref}
    data-sidebar="menu"
    className={cn("flex w-full min-w-0 flex-col gap-1", className)}
    {...props}
  />
));
SidebarMenu.displayName = "SidebarMenu";

const SidebarMenuItem = React.forwardRef<
  HTMLLIElement,
  React.HTMLAttributes<HTMLLIElement>
>(({ className, ...props }, ref) => (
  <li
    ref={ref}
    data-sidebar="menu-item"
    className={cn("group/menu-item relative", className)}
    {...props}
  />
));
SidebarMenuItem.displayName = "SidebarMenuItem";

const sidebarMenuButtonVariants = cva(
  "peer/menu-button relative flex w-full items-center gap-2 overflow-hidden rounded-md px-2 py-1.5 text-sm outline-none ring-sidebar-ring transition-[width,height,padding] hover:bg-sidebar-accent focus-visible:ring-2 active:bg-sidebar-accent disabled:pointer-events-none disabled:opacity-50 group-data-[collapsible=icon]/sidebar-wrapper:!size-8 group-data-[collapsible=icon]/sidebar-wrapper:!p-0 [&>span:last-child]:truncate [&>svg]:size-4 [&>svg]:shrink-0",
  {
    variants: {
      isActive: {
        true: "bg-sidebar-accent text-sidebar-accent-foreground",
        false:
          "text-sidebar-foreground hover:text-sidebar-foreground/80 group-data-[collapsible=icon]/sidebar-wrapper:[&>svg]:-order-1",
      },
      size: {
        default: "h-8",
        sm: "h-7 text-xs",
        lg: "h-12 text-base group-data-[collapsible=icon]/sidebar-wrapper:!p-0",
      },
    },
    compoundVariants: [
      {
        isActive: true,
        size: "sm",
        className: "bg-sidebar-accent",
      },
      {
        isActive: true,
        size: "lg",
        className: "bg-sidebar-accent",
      },
    ],
    defaultVariants: {
      isActive: false,
      size: "default",
    },
  },
);

interface SidebarMenuButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof sidebarMenuButtonVariants> {
  asChild?: boolean;
  tooltip?: string | React.ComponentProps<typeof SidebarMenuButtonTooltip>;
}

const SidebarMenuButton = React.forwardRef<
  HTMLButtonElement,
  SidebarMenuButtonProps
>(
  (
    { asChild = false, isActive = false, size = "default", className, tooltip, ...props },
    ref,
  ) => {
    const Comp = asChild ? Slot : "button";
    const { state } = useSidebar();

    const button = (
      <Comp
        ref={ref}
        data-sidebar="menu-button"
        data-size={size}
        data-active={isActive}
        className={cn(sidebarMenuButtonVariants({ isActive, size }), className)}
        {...props}
      />
    );

    if (!tooltip) {
      return button;
    }

    return (
      <SidebarMenuButtonTooltip {...(typeof tooltip === "string" ? { children: tooltip } : tooltip)}>
        {button}
      </SidebarMenuButtonTooltip>
    );
  },
);
SidebarMenuButton.displayName = "SidebarMenuButton";

const SidebarMenuButtonTooltip = ({
  children,
  ...props
}: React.ComponentProps<typeof SidebarPrimitive.MenuButtonTooltip>) => {
  return (
    <SidebarPrimitive.MenuButtonTooltip {...props}>
      {children}
    </SidebarPrimitive.MenuButtonTooltip>
  );
};

const SidebarMenuAction = React.forwardRef<
  HTMLButtonElement,
  React.HTMLAttributes<HTMLButtonElement> & {
    asChild?: boolean;
    showOnHover?: boolean;
  }
>(
  (
    { className, asChild = false, showOnHover = false, ...props },
    ref,
  ) => {
    const Comp = asChild ? Slot : "button";

    return (
      <Comp
        ref={ref}
        data-sidebar="menu-action"
        className={cn(
          "absolute right-1 top-1/2 display:none rounded-md p-1 outline-none ring-sidebar-ring transition-transform hover:bg-sidebar-accent focus-visible:ring-2 peer-hover/menu-button:display:block group-focus-within/menu-item:display:block group-data-[collapsible=icon]/sidebar-wrapper:hidden",
          showOnHover && "display:block",
          className,
        )}
        {...props}
      />
    );
  },
);
SidebarMenuAction.displayName = "SidebarMenuAction";

const SidebarMenuSub = React.forwardRef<
  HTMLUListElement,
  React.HTMLAttributes<HTMLUListElement>
>(({ className, ...props }, ref) => (
  <ul
    ref={ref}
    data-sidebar="menu-sub"
    className={cn(
      "mx-3.5 flex min-w-0 translate-x-px flex-col gap-1 border-l border-sidebar-border px-2.5 py-0.5 group-data-[collapsible=icon]/sidebar-wrapper:hidden",
      className,
    )}
    {...props}
  />
));
SidebarMenuSub.displayName = "SidebarMenuSub";

const SidebarMenuSubItem = React.forwardRef<
  HTMLLIElement,
  React.HTMLAttributes<HTMLLIElement>
>(({ ...props }, ref) => (
  <li ref={ref} {...props} />
));
SidebarMenuSubItem.displayName = "SidebarMenuSubItem";

const SidebarMenuSubButton = React.forwardRef<
  HTMLAnchorElement,
  React.AnchorHTMLAttributes<HTMLAnchorElement> & {
    asChild?: boolean;
    size?: "sm" | "md";
    isActive?: boolean;
  }
>(
  (
    { asChild = false, size = "md", isActive, className, ...props },
    ref,
  ) => {
    const Comp = asChild ? Slot : "a";

    return (
      <Comp
        ref={ref}
        data-sidebar="menu-sub-button"
        data-size={size}
        data-active={isActive}
        className={cn(
          "relative flex h-7 min-w-0 items-center gap-2 rounded-md px-2 text-xs outline-none ring-sidebar-ring transition-[width,height,padding] hover:bg-sidebar-accent focus-visible:ring-2 active:bg-sidebar-accent disabled:pointer-events-none disabled:opacity-50 data-[active=true]:bg-sidebar-accent data-[active=true]:font-medium aria-disabled:pointer-events-none aria-disabled:opacity-50 group-data-[collapsible=icon]/sidebar-wrapper:hidden [&>svg]:size-4 [&>svg]:shrink-0",
          size === "sm" && "gap-1",
          className,
        )}
        {...props}
      />
    );
  },
);
SidebarMenuSubButton.displayName = "SidebarMenuSubButton";

const Tooltip = React.forwardRef<
  React.ElementRef<typeof SidebarPrimitive.Tooltip>,
  React.ComponentPropsWithoutRef<typeof SidebarPrimitive.Tooltip>
>(({ ...props }, ref) => (
  <SidebarPrimitive.Tooltip ref={ref} {...props} />
));
Tooltip.displayName = "Tooltip";

const TooltipTrigger = React.forwardRef<
  React.ElementRef<typeof SidebarPrimitive.TooltipTrigger>,
  React.ComponentPropsWithoutRef<typeof SidebarPrimitive.TooltipTrigger>
>(({ ...props }, ref) => (
  <SidebarPrimitive.TooltipTrigger ref={ref} {...props} />
));
TooltipTrigger.displayName = "TooltipTrigger";

const TooltipContent = React.forwardRef<
  React.ElementRef<typeof SidebarPrimitive.TooltipContent>,
  React.ComponentPropsWithoutRef<typeof SidebarPrimitive.TooltipContent>
>(({ ...props }, ref) => (
  <SidebarPrimitive.TooltipContent ref={ref} {...props} />
));
TooltipContent.displayName = "TooltipContent";

export {
  Sidebar,
  SidebarProvider,
  SidebarTrigger,
  SidebarRail,
  SidebarInset,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupAction,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarMenuAction,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton,
  useSidebar,
};
