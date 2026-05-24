import { FileText, Database, Tag } from "lucide-react";

export function ProblemCards() {
  return (
    <section className="py-32 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        
        <div className="grid md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="p-8 border border-[#eaeaea] bg-white rounded-xl hover:border-black hover:shadow-sm transition-all duration-300">
            <FileText className="w-8 h-8 mb-6 text-black" strokeWidth={1.5} />
            <h3 className="text-xl font-semibold text-black mb-3">System prompt overflow</h3>
            <p className="text-[#666666] leading-relaxed">
              Stuffing history into the system prompt works for a demo. In production, token limits are hit in week 2.
            </p>
          </div>

          {/* Card 2 */}
          <div className="p-8 border border-[#eaeaea] bg-white rounded-xl hover:border-black hover:shadow-sm transition-all duration-300">
            <Database className="w-8 h-8 mb-6 text-black" strokeWidth={1.5} />
            <h3 className="text-xl font-semibold text-black mb-3">Vector search alone</h3>
            <p className="text-[#666666] leading-relaxed">
              Standard RAG gives you text chunks with no time order and no structural relationships between entities.
            </p>
          </div>

          {/* Card 3 */}
          <div className="p-8 border border-[#eaeaea] bg-white rounded-xl hover:border-black hover:shadow-sm transition-all duration-300">
            <Tag className="w-8 h-8 mb-6 text-black" strokeWidth={1.5} />
            <h3 className="text-xl font-semibold text-black mb-3">Metadata tags</h3>
            <p className="text-[#666666] leading-relaxed">
              Relying on hardcoded JSON metadata tags breaks down as your application scales and relationships become complex.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
