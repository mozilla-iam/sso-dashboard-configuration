require 'yaml'
apps = YAML.load(File.read("apps.yml"))
client_ids = []
spanning_client_ids = []

apps["apps"].each do |app|
	begin

		client_id = app["application"]["client_id"]
		if client_id.nil?
                        url = app["application"]["url"]
                        aal = app["application"]["AAL"]
                        if aal.nil? or aal != "LOW"
                                puts "no client_id and no AAL: LOW for #{url}"
                        else
                                puts "no client_id for #{url}"
                        end
                else
			client_ids.append(client_id)
		end
	rescue
		puts "no client_id"
	end
end


client_ids.each do |client_id|
	count = 0
	apps["apps"].each do |app|
		if app["application"]["client_id"] == client_id or app["application"]["url"].include? client_id
			count += 1
		end
	end

	if count > 1
		spanning_client_ids.append "#{count} #{client_id}"
	end
end

puts spanning_client_ids.uniq
