export class Shadow {
  constructor(color, thickOrThin) {
    this._color = color;
    this._thickOrThin = thickOrThin;
  }

  static thick(color) {
    return new Shadow(color, "thick");
  }

  static thin(color) {
    return new Shadow(color, "thin");
  }

  fatness() {
    switch(this._thickOrThin) {
      case "thick": return "0.2em";
      case "thin": return "0.1em";
      default:
        console.error(`'${this._thickOrThin}' is not a valid shadow thickness`);
    }
  }

  showTop() {
      return "inset 0 " + this.fatness() + " " + this._color;
  }

  showBottom() {
      return "inset 0 -" + this.fatness() + " " + this._color;
  }

  showLeft() {
      return "inset " + this.fatness() + " 0 " + this._color;
  }

  showRight() {
      return "inset -" + this.fatness() + " 0 " + this._color;
  }

  showUnit() {
      const f = this.fatness();
      return "inset " + f + " " + f + " " + this._color +
          ",\ninset -" + f + " -" + f + " " + this._color;
  }
}

function regenerateShadows(cell) {
  if (cell.unitShadow !== undefined) {
    cell.style.boxShadow = cell.unitShadow.showUnit();
    return;
  }
  const decorations = [];
  if (cell.topShadow !== undefined) {
    decorations.push(cell.topShadow.showTop());
  }
  if (cell.bottomShadow !== undefined) {
    decorations.push(cell.bottomShadow.showBottom());
  }
  if (cell.leftShadow !== undefined) {
    decorations.push(cell.leftShadow.showLeft());
  }
  if (cell.rightShadow !== undefined) {
    decorations.push(cell.rightShadow.showRight());
  }
  cell.style.boxShadow = decorations.join(", ");
}

export function addShadow(cell, position, shadow) {
  switch(position) {
    case "top":
      cell.topShadow = shadow;
      break;
    case "bottom":
      cell.bottomShadow = shadow;
      break;
    case "left":
      cell.leftShadow = shadow;
      break;
    case "right":
      cell.rightShadow = shadow;
      break;
    case "unit":
      removeAll(cell);
      cell.unitShadow = shadow;
      break;
    default:
      console.error(`'${position}' is not a valid shadow position`);
  }
  regenerateShadows(cell);
}

export function removeShadow(cell, position) {
  switch(position) {
    case "top":
      delete cell.topShadow;
      break;
    case "bottom":
      delete cell.bottomShadow;
      break;
    case "left":
      delete cell.leftShadow;
      break;
    case "right":
      delete cell.rightShadow;
      break;
    case "unit":
      delete cell.unitShadow;
      break;
    default:
      console.error(`'${position}' is not a valid shadow position`);
  }
  regenerateShadows(cell);
}

export function removeAll(cell) {
  delete cell.topShadow;
  delete cell.bottomShadow;
  delete cell.leftShadow;
  delete cell.rightShadow;
  delete cell.unitShadow;
  cell.style.boxShadow = "";
}
