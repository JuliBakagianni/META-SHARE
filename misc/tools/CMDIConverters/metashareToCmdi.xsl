<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.clarin.eu/cmd/" 
xmlns:ms="http://www.ilsp.gr/META-XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xalan="http://xml.apache.org/xslt"  xmlns:date="http://exslt.org/dates-and-times" 
exclude-result-prefixes="ms xalan date" >
	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" xalan:indent-amount="4"/>
	<xsl:strip-space elements="*"/>

	<xsl:template match="*">
    	<xsl:element name="{local-name(.)}">
    		<xsl:apply-templates select="@* | node()"/>
    	</xsl:element>
    </xsl:template>

    <xsl:template match ="@*" >
			<xsl:if test="local-name() = 'lang'">
				<xsl:attribute name ="xml:lang">
					<xsl:value-of select ="." />
				</xsl:attribute>
			</xsl:if>
	</xsl:template>

	<xsl:template name="personOrOrganizationInfo">
		<xsl:choose>
			<xsl:when test="ms:personInfo">
				<xsl:element name="{concat(local-name(), 'Person')}">
					<xsl:element name="role">
						<xsl:value-of select ="local-name()"/>
					</xsl:element>
					<xsl:element name="{local-name(ms:personInfo)}">
						<xsl:for-each select="ms:personInfo/child::*">
							<xsl:sort select="not(child::*)" order="descending"/>
							<xsl:choose>
								<xsl:when test="self::ms:affiliation">
									<xsl:element name="{local-name()}">
										<xsl:element name="role">
											<xsl:value-of select ="local-name()"/>
										</xsl:element>
										<xsl:element name="organizationInfo">
											<xsl:apply-templates select="child::*"/>
										</xsl:element>
									</xsl:element>
								</xsl:when>
								<xsl:otherwise>
									<xsl:apply-templates select="."/>
								</xsl:otherwise>
							</xsl:choose>
						</xsl:for-each>
					</xsl:element>
				</xsl:element>
			</xsl:when>
			<xsl:otherwise>
				<xsl:element name="{concat(local-name(), 'Organization')}">
					<xsl:element name="role">
						<xsl:value-of select ="local-name()"/>
					</xsl:element>
					<xsl:apply-templates select="child::*"/>
				</xsl:element>			
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="reportInfo">
		<xsl:choose>
			<xsl:when test="child::ms:documentUnstructured">
				<xsl:element name="{concat(local-name(), 'Unstructured')}">
					<xsl:element name="role">
						<xsl:value-of select ="local-name()"/>
					</xsl:element>
					<xsl:apply-templates select="node()"/>
				</xsl:element>
			</xsl:when>
			<xsl:otherwise>
				<xsl:element name="{concat(local-name(), 'Structured')}">
					<xsl:element name="role">
						<xsl:value-of select ="local-name()"/>
					</xsl:element>
					<xsl:apply-templates select="node()"/>
				</xsl:element>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

    <xsl:template name="sizeInfoPerCategory">
        <xsl:element name="{local-name()}">
            <xsl:element name="role">
                <xsl:value-of select ="local-name()"/>
            </xsl:element>
            <xsl:element name="sizeInfo">
                <xsl:apply-templates select="child::*"/>
            </xsl:element>
        </xsl:element>
    </xsl:template>

    <xsl:template match="ms:contactPerson | ms:metadataCreator">
        <xsl:element name="{local-name()}">
            <xsl:element name="role">
                <xsl:value-of select ="local-name()"/>
            </xsl:element>
            <xsl:element name="personInfo">
                <xsl:for-each select="child::*">
                    <xsl:sort select="not(child::*)" order="descending"/>
                    <xsl:choose>
                        <xsl:when test="self::ms:affiliation">
                            <xsl:element name="affiliation">
                                <xsl:element name="role">
                                    <xsl:value-of select ="local-name()"/>
                                </xsl:element>
                                <xsl:element name="organizationInfo">
                                    <xsl:for-each select="child::*">
                                        <xsl:apply-templates select="."/>
                                    </xsl:for-each>
                                </xsl:element>
                            </xsl:element>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:apply-templates select="."/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
            </xsl:element>
        </xsl:element>
    </xsl:template>

	<xsl:template match="ms:iprHolder | ms:distributionRightsHolder | ms:licensor | ms:validator | ms:resourceCreator | 
	   ms:annotator | ms:recorder | ms:evaluator">
        <xsl:call-template name="personOrOrganizationInfo"/>
    </xsl:template>

	<xsl:template match="ms:sizePerValidation">
		<xsl:element name="{local-name()}">
			<xsl:element name="role">
				<xsl:value-of select="local-name()"/>
			</xsl:element>
			<xsl:element name="sizeInfo">
				<xsl:apply-templates select="child::*"/>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	
	<xsl:template match="ms:validationReport | ms:usageReport | ms:documentation | ms:annotationManual | ms:evaluationReport">
        <xsl:call-template name="reportInfo"/>
    </xsl:template>

	<xsl:template match="ms:usageProject | ms:fundingProject">
		<xsl:element name="{local-name()}">
			<xsl:element name="role">
				<xsl:value-of select ="local-name()"/>
			</xsl:element>
			<xsl:element name="projectInfo">
				<xsl:apply-templates select="node()"/>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	
	<xsl:template match="ms:sizePerLanguage | ms:sizePerLanguageVariety | ms:sizePerAnnotation | ms:sizePerAudioFormat | 
	   ms:sizePerVideoFormat | ms:sizePerImageFormat | ms:sizePerModality | ms:sizePerTextFormat | ms:sizePerCharacterEncoding | 
	   ms:sizePerDomain | ms:sizePerTextClassification | ms:sizePerTimeCoverage | ms:sizePerGeographicCoverage | 
	   ms:sizePerAudioFormat | ms:sizePerAudioClassification | ms:sizePerVideoFormat | ms:sizePerVideoClassification | 
	   ms:sizePerImageClassification | ms:sizePerImageFormat | ms:sizePerTextNumericalFormat">
        <xsl:call-template name="sizeInfoPerCategory"/>
    </xsl:template>

	<xsl:template match="ms:resourceInfo" name="resourceInfo">
		<xsl:text>
</xsl:text>
		<CMD>
			<xsl:attribute name="CMDVersion">1.1</xsl:attribute>
			<xsl:attribute name="xsi:schemaLocation">
				<xsl:choose>
					<xsl:when test="ms:resourceComponentType/ms:corpusInfo">
						<xsl:text>http://www.clarin.eu/cmd/ http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/clarin.eu:cr1:p_1361876010571/xsd</xsl:text>
					</xsl:when>
					<xsl:when test="ms:resourceComponentType/ms:toolServiceInfo">
						<xsl:text>http://www.clarin.eu/cmd/ http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/clarin.eu:cr1:p_1360931019836/xsd</xsl:text>
					</xsl:when>
					<xsl:when test="ms:resourceComponentType/ms:languageDescriptionInfo">
						<xsl:text>http://www.clarin.eu/cmd/ http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/clarin.eu:cr1:p_1361876010554/xsd</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:text>http://www.clarin.eu/cmd/ http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/clarin.eu:cr1:p_1355150532312/xsd</xsl:text>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<Header>
				<MdCreator>metashareToCmdi.xsl</MdCreator>
				<MdCreationDate>
					<xsl:value-of select="substring(date:date(), 1, 10)"/>
				</MdCreationDate>
				<MdProfile>
					<xsl:choose>
						<xsl:when test="ms:resourceComponentType/ms:corpusInfo">
							<xsl:text>clarin.eu:cr1:p_1361876010571</xsl:text>
						</xsl:when>
						<xsl:when test="ms:resourceComponentType/ms:toolServiceInfo">
							<xsl:text>clarin.eu:cr1:p_1360931019836</xsl:text>
						</xsl:when>
						<xsl:when test="ms:resourceComponentType/ms:languageDescriptionInfo">
							<xsl:text>clarin.eu:cr1:p_1361876010554</xsl:text>
						</xsl:when>
						<xsl:otherwise>
							<xsl:text>clarin.eu:cr1:p_1355150532312</xsl:text>
						</xsl:otherwise>
					</xsl:choose>
				</MdProfile>
			</Header>
			<Resources>
				<ResourceProxyList/>
				<JournalFileProxyList/>
				<ResourceRelationList/>
			</Resources>
			<Components>
				<resourceInfo>
					<xsl:for-each select="child::*[not(self::ms:resourceComponentType)]">
						<xsl:apply-templates select="."/>
					</xsl:for-each>
					<xsl:if test="ms:resourceComponentType/ms:corpusInfo">
						<xsl:apply-templates select="//ms:corpusInfo"/>
					</xsl:if>
					<xsl:if test="ms:resourceComponentType/ms:toolServiceInfo">
						<xsl:apply-templates select="//ms:toolServiceInfo"/>
					</xsl:if>
					<xsl:if test="ms:resourceComponentType/ms:languageDescriptionInfo">
						<xsl:apply-templates select="//ms:languageDescriptionInfo"/>
					</xsl:if>
					<xsl:if test="ms:resourceComponentType/ms:lexicalConceptualResourceInfo">
						<xsl:apply-templates select="//ms:lexicalConceptualResourceInfo"/>
					</xsl:if>
				</resourceInfo>
			</Components>
		</CMD>
	</xsl:template>
</xsl:stylesheet>
