import React, { useEffect, useState } from 'react';

const DEFUALT_STYLES = { height: 0, width: 0 };

/**
 *
 * @param {String} elementId
 * Creates a placeholder for an element equal to the size of the element
 * with the given id.
 */

function ElementSpacePlaceholder({
  elementId,
  className,
}: { elementId: string; className?: string }) {
  const [style, setStyle] = useState(DEFUALT_STYLES);

  useEffect(() => {
    const element = document.getElementById(elementId);
    if (element) {
      setStyle({
        height: element.offsetHeight,
        width: element.offsetWidth,
      });
    } else {
      setStyle(DEFUALT_STYLES);
    }
  }, [elementId]);

  if (elementId) {
    return (
      <div
        className={className}
        style={style}
      />
    );
  } else {
    return null;
  }
}

export default ElementSpacePlaceholder;