'use client';

import { useRef, useState } from 'react';
import Link from 'next/link';

export default function SpotlightCard({ children, href, className = "" }) {
    const divRef = useRef(null);
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [opacity, setOpacity] = useState(0);

    const handleMouseMove = (e) => {
        if (!divRef.current) return;
        const rect = divRef.current.getBoundingClientRect();
        setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
    };

    const handleMouseEnter = () => setOpacity(1);
    const handleMouseLeave = () => setOpacity(0);

    const Wrapper = href ? Link : 'div';
    const props = href ? { href } : {};

    return (
        <Wrapper
            {...props}
            ref={divRef}
            onMouseMove={handleMouseMove}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            className={`relative overflow-hidden rounded-[16px] bg-[#1c1c1e] border border-[var(--system-gray-5)] group cursor-pointer ${className}`}
        >
            <div
                className="pointer-events-none absolute -inset-px opacity-0 transition duration-300 group-hover:opacity-100"
                style={{
                    background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(255,255,255,0.06), transparent 40%)`,
                }}
            />
            <div className="relative">{children}</div>
        </Wrapper>
    );
}
