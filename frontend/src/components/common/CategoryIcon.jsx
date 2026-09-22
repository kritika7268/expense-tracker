import React from 'react';
import {
  Utensils,
  Car,
  ShoppingBag,
  Receipt,
  Film,
  GraduationCap,
  HeartPulse,
  Plane,
  Repeat,
  MoreHorizontal,
  Briefcase,
  Laptop,
  Building,
  BookOpen,
  Gift,
  DollarSign,
  Coffee,
  Home,
  Smartphone,
  Zap,
  Tag,
} from 'lucide-react';

const ICON_MAP = {
  Utensils,
  Car,
  ShoppingBag,
  Receipt,
  Film,
  GraduationCap,
  HeartPulse,
  Plane,
  Repeat,
  MoreHorizontal,
  Briefcase,
  Laptop,
  Building,
  BookOpen,
  Gift,
  DollarSign,
  Coffee,
  Home,
  Smartphone,
  Zap,
  Tag,
};

export const CategoryIcon = ({ name = 'Tag', className = 'w-5 h-5' }) => {
  const IconComponent = ICON_MAP[name] || Tag;
  return <IconComponent className={className} />;
};

export default CategoryIcon;
