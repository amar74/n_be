import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import { BreadcrumbItem } from '../../AccountDetailsPage.types';

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <div className="flex items-center gap-1 text-[16px] font-inter font-medium">
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <ChevronRight className="h-5 w-5 text-[#a7a7a7] rotate-90" />
          )}
          {item.href ? (
            <Link 
              to={item.href}
              className="text-[#a7a7a7] hover:text-[#0f0901] transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className={index === items.length - 1 ? "text-[#0f0901]" : "text-[#a7a7a7]"}>
              {item.label}
            </span>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
