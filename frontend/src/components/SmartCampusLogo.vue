<template>
  <svg
    class="smart-campus-logo"
    viewBox="0 0 580 270"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    aria-label="Smart CAMPUS"
    focusable="false"
  >
    <g aria-hidden="true">
      <text class="smart-campus-logo__smart" x="4" y="158">Smart</text>
      <text
        class="smart-campus-logo__campus"
        x="0"
        y="261"
        textLength="524"
        lengthAdjust="spacingAndGlyphs"
      >CAMPUS</text>

      <!-- The two slate tones give the mortarboard its folded shape. -->
      <path
        fill="#647780"
        d="M 374 82 L 456 115 L 538 82 L 538 128
           Q 456 190 374 128 Z"
      />
      <path fill="#536872" d="M 374 82 L 414 99 L 396 143 Q 383 136 374 128 Z" />
      <path fill="#536872" d="M 333 51 L 456 1 L 578 51 L 456 101 Z" />
      <path fill="#647780" d="M 456 1 L 578 51 L 456 101 L 433 91 Z" />

      <!-- A slim gold cord and tassel complete the graduation cap. -->
      <path
        d="M 564 69 L 564 111"
        fill="none"
        stroke="#eed46c"
        stroke-width="4"
        stroke-linecap="round"
      />
      <circle cx="564" cy="115" r="7" fill="#f1d56b" />
      <path
        fill="#f1d56b"
        d="M 556 129 Q 564 125 572 129 L 575 179
           L 569 175 L 565 183 L 560 178 L 554 183 Z"
      />
    </g>
  </svg>
</template>

<style scoped>
.smart-campus-logo {
  display: block;
  width: 266px;
  max-width: 100%;
  height: auto;
  flex-shrink: 0;
  overflow: visible;
  color: #171919;
}

.smart-campus-logo__smart,
.smart-campus-logo__campus {
  fill: currentColor;
  font-family: Arial, Helvetica, sans-serif;
}

.smart-campus-logo__smart {
  font-size: 124px;
  font-weight: 400;
}

.smart-campus-logo__campus {
  font-size: 128px;
  font-weight: 700;
}
</style>
